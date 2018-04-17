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


class MyoDataProcess(multiprocessing.Process):

    def __init__(self, thread_name, mac_addr, iface, timeout=30, sleep_interval=1):
        multiprocessing.Process.__init__(self)
        # initial status
        self.status = MyoStatus.PENDING
        self.thread_name = thread_name

        self.mac_addr = mac_addr
        self.myo = None

        self.arm_type = Arm.UNKNOWN

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

        arm_delegate = MyoArmDelegate(self)

        while not self.kill_received and self.status != MyoStatus.CONNECTED:
            if self.myo.connect(init_delegate=arm_delegate, iface=self.iface) == MyoStatus.PENDING:
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
        self.add_data_handler()

    def get_arm_type(self):

        while not self.kill_received and self.arm_type == Arm.UNKNOWN:
            self.myo.run(1)

        self.logger.error("%s: Get myo arm type: %s", self.thread_name, self.arm_type)

    def config_myo(self, emg_enable=True, imu_enable=True, emg_raw_enable=True):
        config = MyoConfig()
        config.emg_enable = emg_enable
        config.imu_enable = imu_enable
        config.emg_raw_enable = emg_raw_enable
        self.myo.config_myo(config)

    def add_data_handler(self, handler=None):
        pass
        # if handler is None:
        #     handler = MyoThreadHandler(self)
        # self.myo.add_emg_handler(handler.emg_handler)
        # self.myo.add_imu_handler(handler.imu_handler)
        # self.myo.add_emg_raw_handler(handler.emg_raw_handler)

    def get_data(self):
        try:
            return self.emg_pool.get(), self.imu_data_pool.get(), self.emg_raw_data_pool.get()
        except queue.Empty:
            return None, None, None


class MyoArmDelegate(DefaultDelegate):

    def __init__(self, myo_thread: MyoDataProcess):
        DefaultDelegate.__init__(self)
        self.arm_type = Arm.UNKNOWN
        self.thread = myo_thread

    def handleNotification(self, cHandle, data):
        print(cHandle, data)
        if cHandle == MyoHandler.ARM_DATA_HANDLE.value:
            typ, val, xdir, pose, sync_result = unpack('3BHB', data)
            if typ == MyoClassifierEventType.ARM_SYNCED.value:
                self.arm_handler(Arm(val), XDirection(xdir))

    def arm_handler(self, arm, xdir):
        self.arm_type = arm
        print(self.arm_type)
        self.thread.arm_type = self.arm_type


class MyoScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", scanEntry.addr)
        elif isNewData:
            print("Received new data from %s" % scanEntry.addr)


class MyoHub:

    def __init__(self, myo_count=2, handler: MyoDefaultHandler = None):
        self.logger = logging.getLogger("myo")
        self.logger.setLevel(logging.DEBUG)
        signal.signal(signal.SIGINT, self.disconnect)
        self.myo_count = myo_count
        self.myo_thread_pool = []
        self.myo_list = self.scan_myos(myo_count=myo_count, scan_time=5.0, iface=1)
        self.init_myos(self.myo_list)

        self.handler = handler
        self.running = False

    def init_myos(self, myo_list):
        for idx, dev in enumerate(myo_list):
            myo_thread = MyoDataProcess("myo" + str(idx), dev.addr, iface=idx)
            try:
                myo_thread.add_data_handler(self.handler)
            except AttributeError:
                pass
            self.myo_thread_pool.append(myo_thread)

    def run(self):
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
        scan myo in scan_time seconds
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
                "Cannot found enough myos, find count: %s, need count: %s" % (len(myo_lists), myo_count))
        return myo_lists

    def add_data_handlers(self, handler):
        for thread in self.myo_thread_pool:
            thread.add_data_handler(handler)


if __name__ == '__main__':
    hub = MyoHub(myo_count=1)
    hub.run()
