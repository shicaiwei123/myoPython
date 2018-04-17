"""
MyoHub controls two Myo armbands which one is as left arm and the other is as right arm
It returns left arm data and right arm data
"""
import enum
import logging
import multiprocessing
import os
import queue
import signal
import sys
import time

from Bean.myo_handler import MyoDefaultHandler
from Bean.myo_info import MyoHandler, MyoClassifierEventType

sys.path.append(os.path.abspath(os.path.pardir))

from Bean.myo import MyoRaw, Arm, unpack, XDirection
from Bean.myo_config import MyoConfig
from bluepy.btle import Scanner, DefaultDelegate, BTLEException


class MyoStatus(enum.Enum):
    PENDING = 0
    SCANNING = 1
    CONNECTING = 2
    CONNECTED = 3
    DISCONNECTED = 4


class MyoDataDelegate(DefaultDelegate):

    def __init__(self):
        DefaultDelegate.__init__(self)
        self.arm_type = Arm.UNKNOWN
        self.emg_queue = queue.Queue()
        self.imu_queue = queue.Queue()

    def handleNotification(self, cHandle, data):
        print(cHandle, data)
        if cHandle == MyoHandler.ARM_DATA_HANDLE.value:
            typ, val, xdir, pose, sync_result = unpack('3BHB', data)
            if typ == MyoClassifierEventType.ARM_SYNCED.value:
                self.arm_handler(Arm(val), XDirection(xdir))

        if cHandle == MyoHandler.EMG_DATA_HANDLE.value:
            self.emg_queue.put()

        if cHandle == MyoHandler.IMU_DATA_HANDLE.value:
            self.imu_queue.put()

    def arm_handler(self, arm, xdir):
        self.arm_type = arm
        print(self.arm_type)
        self.thread.arm_type = self.arm_type


class MyoDataProcess(multiprocessing.Process):

    def __init__(self, thread_name, mac_addr, iface, data_delegate: MyoDataDelegate, timeout=30, sleep_interval=1):
        multiprocessing.Process.__init__(self)
        # initial status
        self.status = MyoStatus.PENDING
        self.thread_name = thread_name

        self.mac_addr = mac_addr
        self.myo = None

        self.data_delegate = data_delegate

        self.logger = logging.getLogger("myo")
        self.logger.setLevel(logging.INFO)

        self.kill_received = False
        self.timeout = timeout
        self.sleep_interval = sleep_interval
        self.iface = iface

    def run(self):
        """
        connect to a myo and read data from it
        when myo is disconnected, change to scanning status
        :return:
        """
        # if adapter is scanning, wait for ending
        while not self.kill_received:
            try:
                if self.myo is None and (
                        self.status == MyoStatus.PENDING or self.status == MyoStatus.DISCONNECTED
                ):
                    self.connect_myo()
                    self.init_myo()
                else:
                    self.myo.run(1)

            except BTLEException as e:
                # TODO: Change Type of Exception to BLE Exception
                self.status = MyoStatus.DISCONNECTED
                self.logger.info("%s: Myo is disconnected" % self.thread_name)
                self.myo = None

        if self.myo is not None:
            self.myo.disconnect()
        self.logger.info("%s: thread exit" % self.thread_name)

    def connect_myo(self):
        myo_arm_config = MyoConfig()
        myo_arm_config.classifier_enable = True
        self.myo = MyoRaw(self.mac_addr, config=myo_arm_config)
        self.status = MyoStatus.CONNECTING

        while not self.kill_received and self.status != MyoStatus.CONNECTED:
            if self.myo.connect(init_delegate=self.data_delegate, iface=self.iface) == MyoStatus.PENDING:
                self.logger.warning("%s: Cannot connect myo, wait for next loop", self.thread_name)
                time.sleep(self.sleep_interval)
                continue
            else:
                # connect succeed
                self.status = MyoStatus.CONNECTED
                self.logger.info("%s: Myo is connected, iface: %s" % (self.thread_name, self.iface))

    def init_myo(self):
        if self.myo is None:
            return
        self.get_arm_type()

    def get_arm_type(self):

        while not self.kill_received and self.data_delegate.arm_type == Arm.UNKNOWN:
            self.myo.run(1)

        self.logger.error("%s: Get myo arm type: %s", self.thread_name, self.data_delegate.arm_type)

    def config_myo(self, emg_enable=True, imu_enable=True, emg_raw_enable=True):
        config = MyoConfig()
        config.emg_enable = emg_enable
        config.imu_enable = imu_enable
        config.emg_raw_enable = emg_raw_enable
        self.myo.config_myo(config)


class MyoHub:

    def __init__(self, myo_count=2):
        self.logger = logging.getLogger("myo")
        self.logger.setLevel(logging.DEBUG)
        signal.signal(signal.SIGINT, self.disconnect)

        self.myo_count = myo_count
        self.myo_thread_pool = []
        self.myo_delegate_pool = []

        self.myo_list = self.scan_myos(myo_count=myo_count, scan_time=5.0, iface=1)
        self.init_myos(self.myo_list)

        self.running = False

    def init_myos(self, myo_list):
        """
        初始化Myo,创建多个线程，传入指定的Delegate
        :param myo_list:
        :return:
        """
        for idx, dev in enumerate(myo_list):
            myo_delegate = MyoDataDelegate()
            myo_thread = MyoDataProcess("myo-" + str(idx), dev.addr, iface=idx, data_delegate=myo_delegate)
            self.myo_thread_pool.append(myo_thread)
            self.myo_delegate_pool.append(myo_delegate)

    def run(self):
        """
        启动创建的Myo线程
        :return:
        """
        self.running = True
        for thread in self.myo_thread_pool:
            thread.start()

    def disconnect(self, signum=None, frame=None):
        logging.info("Waiting for thread exit......")
        for thread in self.myo_thread_pool:
            thread.kill_received = True
        self.running = False

    def scan_myos(self, myo_count=2, scan_time=10.0, iface=0):
        """
        扫描Myo
        :param myo_count:
        :param scan_time:
        :param iface: index of hci
        :return: list of myos(ScanEntity Class)
        """
        myo_lists = []

        if not isinstance(myo_count, int):
            self.logger.warning("myo_count parameter is not Integer, use myo_count=2")
            myo_count = 2
        if not isinstance(scan_time, float):
            self.logger.warning("scan_time parameter is not Float, use scan_time=10.0")
            scan_time = 10.0
        if not isinstance(iface, int):
            self.logger.warning("iface parameter is not Integer, use iface=0")
            iface = 0

        scanner = Scanner(iface=iface).withDelegate(MyoScanDelegate())
        devices = scanner.scan(scan_time)

        for dev in devices:
            if dev.getValueText(6) == "4248124a7f2c4847b9de04a9010006d5":
                # find myo
                myo_lists.append(dev)
                self.logger.info("Discovered myo: %s, name: %s" % (dev.addr, dev.getValueText(9)))
                continue
        if len(myo_lists) != myo_count:
            self.logger.warning(
                "Cannot found enough myos, find count: %s, need count: %s" % (len(myo_lists), myo_count)
            )
        return myo_lists

    def get_data(self):
        if self.myo_count == 1:
            try:
                emg_data = self.myo_delegate_pool[0].emg_queue.get()
                imu_data = self.myo_delegate_pool[0].imu_queue.get()
                return emg_data, imu_data
            except queue.Empty:
                return None, None
        else:
            # 两个myo
            data_list = []
            for delegate in self.myo_delegate_pool:
                if len(data_list) == 0 and delegate.arm_type == Arm.LEFT:
                    try:
                        data_list.append((delegate.emg_queue.get(), delegate.imu_queue.get()))
                    except queue.Empty:
                        data_list.append((None, None))
                        continue
                elif len(data_list) != 0 and delegate.arm_type == Arm.RIGHT:
                    try:
                        data_list.append((delegate.emg_queue.get(), delegate.imu_queue.get()))
                    except queue.Empty:
                        data_list.append((None, None))
                        continue
            return data_list


class MyoScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", scanEntry.addr)
        elif isNewData:
            print("Received new data from %s" % scanEntry.addr)


if __name__ == '__main__':
    hub = MyoHub(myo_count=1)
    hub.run()
