"""
MyoHub controls two Myo armbands which one is as left arm and the other is as right arm
It returns left arm data and right arm data
"""
import enum
import logging
import sys, os, signal
import re
import multiprocessing
import time
import queue

sys.path.append(os.path.abspath(os.path.pardir))

import serial

from Bean.myo_packet import MyoUnlockMode


from Bean.myo import MyoRaw, MyoStatus, Arm
from Bean.myo_config import MyoConfig
from serial.tools.list_ports import comports


class MyoThreadStatus(enum.Enum):
    PENDING = 0
    SCANNING = 1
    CONNECTING = 2
    CONNECTED = 3
    DISCONNECTED = 4


class MyoDataProcess(multiprocessing.Process):

    def __init__(self, thread_name, tty, timeout=30, sleep_interval=1):
        multiprocessing.Process.__init__(self)
        # initial status
        self.status = MyoThreadStatus.PENDING
        self.thread_name = thread_name

        self.tty = tty
        self.myo = None
        self.arm_type = Arm.UNKNOWN
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.kill_received = False
        self.timeout = timeout
        self.sleep_interval = sleep_interval

        self.emg_pool = queue.Queue()
        self.imu_data_pool = queue.Queue()
        self.emg_raw_data_pool = queue.Queue()

    def run(self):
        """
        connect to a myo and read data from it
        when myo is disconnected, change to scanning status
        :return:
        """
        # if adapter is scanning, wait for ending
        while not self.kill_received:
            try:
                if self.myo is None and (self.status == MyoThreadStatus.PENDING or self.status == MyoThreadStatus.DISCONNECTED):
                    self.connect_myo()
                    self.init_myo()
                else:
                    self.myo.run(1)

            except serial.SerialException as e:
                # TODO: Change Type of Exception to Serial Exception
                self.status = MyoThreadStatus.DISCONNECTED
                self.logger.info("%s: Myo is disconnected" % self.thread_name)
                self.myo = None

        if self.myo is not None:
            self.myo.normal_sleep(self.myo.conn)
            self.myo.set_lock(self.myo.conn, MyoUnlockMode.LOCK_TIMED)
            self.myo.disconnect()
        self.logger.info("%s: thread exit" % self.thread_name)

    def connect_myo(self):
        myo_arm_config = MyoConfig()
        myo_arm_config.arm_enable = True
        self.myo = MyoRaw(self.tty, config=myo_arm_config)
        self.status = MyoThreadStatus.CONNECTING

        while not self.kill_received and self.status != MyoThreadStatus.CONNECTED:
            if self.myo.connect() == MyoStatus.PENDING:
                self.logger.warning("%s: Cannot connect myo, wait for next loop", self.thread_name)
                time.sleep(self.sleep_interval)
                continue
            else:
                # connect succeed
                self.status = MyoThreadStatus.CONNECTED
                self.logger.info("%s: Myo is connected", self.thread_name)

    def init_myo(self):
        if self.myo is None:
            return
        self.get_arm_type()
        self.add_data_handler()

    def get_arm_type(self):

        handler = MyoThreadHandler(self)
        self.myo.add_arm_handler(handler.arm_handler)

        while not self.kill_received and handler.arm_type == Arm.UNKNOWN:
            self.myo.run(1)

        self.myo.remove_arm_handler(handler.arm_handler)
        self.arm_type = handler.arm_type
        self.logger.info("%s: Get myo arm type: %s", self.thread_name, self.arm_type)

    def add_data_handler(self, emg_enable=True, imu_enable=True, emg_raw_enable=False):
        handler = MyoThreadHandler(self)
        config = MyoConfig()
        config.emg_enable = emg_enable
        config.imu_enable = imu_enable
        config.emg_raw_enable = emg_raw_enable
        self.myo.config_myo(config)
        self.myo.add_emg_handler(handler.emg_handler)
        self.myo.add_imu_handler(handler.imu_handler)
        self.myo.add_emg_raw_handler(handler.emg_raw_handler)


class MyoThreadHandler:
    def __init__(self, myo_thread: MyoDataProcess):
        self.arm_type = Arm.UNKNOWN
        self.thread = myo_thread

    def arm_handler(self, arm, xdir):
        self.arm_type = arm

    def emg_handler(self, emg):
        self.thread.emg_pool.put(emg)
        self.thread.logger.info("%s: emg_data: %s", self.thread.name, emg)

    def imu_handler(self, quat, acc, gyro):
        self.thread.imu_data_pool.put((quat, acc, gyro))
        self.thread.logger.info("%s: imu_data: %s", self.thread.name, (quat, acc, gyro))

    def emg_raw_handler(self, emg_raw_data):
        self.thread.emg_raw_data_pool.put(emg_raw_data)


class MyoHub:

    def __init__(self, config=None, myo_count=2):

        self.myo_thread_pool = []
        self.init_myos(myo_count=myo_count)
        self.kill_received = False
        signal.signal(signal.SIGINT, self.disconnect)

    @staticmethod
    def check_comport(port_name):
        """
        check whether specific port exists in the comport list
        :param port_name: specific port name
        :return:
        """
        port_name_list = [p[0] for p in comports()]
        return port_name in port_name_list

    @staticmethod
    def detect_ttys(myo_count=2):
        tty_list = list()

        for p in comports():
            if re.search(r'PID=2458:0*1', p[2]) and p[0] not in tty_list:
                tty_list.append(p[0])
        if len(tty_list) < myo_count:
            raise ValueError("Two Myo dongles not found!")
        # return tty_list[0], tty_list[1]
        return tty_list[0:myo_count]

    def init_myos(self, myo_count=2, wait_time=10000):
        """
        Connect two myo armbands and recognize left myo and right myo

        :param myo_count: 连接的Myo数量
        """

        tty_list = self.detect_ttys(myo_count)

        for tty in tty_list:
            if not (self.check_comport(tty)):
                raise ValueError("No COM ports %s" % tty)

        for index, tty in enumerate(tty_list):
            myo_thread = MyoDataProcess("MyoThread-%s" % index, tty)
            myo_thread.daemon = True
            self.myo_thread_pool.append(myo_thread)

    def run(self, timeout=1):
        for thread in self.myo_thread_pool:
            thread.start()
        while not self.kill_received:
            pass

    def disconnect(self, signum, frame):
        logging.info("Waiting for thread exit......")
        for thread in self.myo_thread_pool:
            thread.kill_received = True
        self.kill_received = True


if __name__ == '__main__':
    hub = MyoHub(myo_count=1)
    hub.run()
