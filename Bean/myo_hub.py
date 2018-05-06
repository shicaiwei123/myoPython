"""
MyoHub controls two Myo armbands which one is as left arm and the other is as right arm
It returns left arm data and right arm data
"""
import sys
import os
import multiprocessing
import re
import logging
import queue
import time

sys.path.append(os.path.abspath(os.path.pardir))

from Bean.myo import MyoRaw
from Bean.myo_config import MyoConfig
from myo_info import Arm
from serial.tools.list_ports import comports

class MyoDataProcess(multiprocessing.Process):
    """
    负责判断Myo的手臂类型，之后收集数据，将数据通过queue.Queue传到MyoHub中进行缓存
    """
    class ArmHandler(object):
        def __init__(self):
            self.arm_type = Arm.UNKNOWN
        
        def arm_handler(self, arm, xdir):
            self.arm_type = arm

    def __init__(self, process_name, serial_port, data_queue, lock, timeout=30, mac_addr=""):
        """
        初始化Myo进程

        :param process_name: str, 进程名称
        :param serial_port: str, 进程对应的串口名称
        :param data_queue: queue.Queue, 用于传输数据到MyoHub的queue
        :param timeout: int, 超时时间
        :param mac_addr: str, 默认为空，此时当串口扫描到任意一个Myo手环的时候都会连接，如果不为空，则当扫描到指定Mac地址手环的时候才会连接 
        """
        multiprocessing.Process.__init__(self)

        self.lock = lock
        self.process_name = process_name
        self.logger = self.config_logger(self.process_name)

        self.data_queue = data_queue
        self.timeout = timeout
        self.serial_port = serial_port
        self.mac_addr = mac_addr

        self.myo = None

        self.kill_received = False
        self.arm_type = Arm.UNKNOWN

    def run(self):
        """
        先连接到手环，然后一直循环，直到kill_received标志位为True
        """
        # while not self.kill_received:
        if self.myo is None:
            self.connect_myo()
        if self.myo is not None:
            self.init_myo()
        
    def config_logger(self, logger_name=__name__):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        return logger

    def connect_myo(self):
        if self.myo is None:
            self.myo = MyoRaw(self.serial_port, mac_address=self.mac_addr)
        try:
            self.lock.acquire()
            self.myo.connect(timeout=self.timeout)
            self.lock.release()
        except TimeoutError as e:
            self.myo = None
            self.logger.error("Cannot connect myo through %s, %s exit", self.serial_port, self.process_name)

    def disconnect_myo(self):
        self.myo.disconnect()
    
    def init_myo(self):
        if self.myo is None:
            return
        self.get_myo_arm_type()
        if self.arm_type == Arm.UNKNOWN:
            return
        # 打开Myo数据开关
        self.start_get_data()

    def config_myo(self, arm_enable=True, emg_enable=True, imu_enable=True):
        config = MyoConfig()
        config.arm_enable = arm_enable
        config.emg_enable = emg_enable
        config.imu_enable = imu_enable
        self.myo.config_myo(config)

    def get_myo_arm_type(self, timeout=30):
        """
        获得Myo手环的手臂类型
        :param timeout: int, 超时时间
        """
        myo_arm_handler = self.ArmHandler()
        self.myo.add_arm_handler(myo_arm_handler.arm_handler)
        self.config_myo(arm_enable=True)
        self.logger.info("Waiting for myo returns its arm type, please wave out and hold to sync")
        start_time = time.time()
        while not self.kill_received and time.time() - start_time < timeout and myo_arm_handler.arm_type == Arm.UNKNOWN:
            self.myo.run(1)
        if myo_arm_handler.arm_type == Arm.UNKNOWN:
            self.logger.warning("Waiting for myo timeout!")
        else:
            self.arm_type = myo_arm_handler.arm_type
            self.logger.info("Get myo arm type: %s", myo_arm_handler.arm_type)

    def start_get_data():
        """
        开始获得数据
        """
        
    
class MyoHub:

    def __init__(self, config=None, tty_left=None, tty_right=None):
        print("Init two myo armbands")
        self.left_myo, self.right_myo = self.init_myos(tty_left, tty_right)
        self.config = config

        if self.left_myo is None and self.right_myo is None:
            raise ValueError("Cannot get two myo armbands' arm type")

        if self.config is None:
            self.init_config()

        # self.add_data_handlers()
        # open two threads to get data
        # self.left_myo.config_myo(self.config)
        # self.right_myo.config_myo(self.config)

    def init_config(self):
        """
        return initial configure
        :return:
        """
        self.config = MyoConfig()
        self.config.open_all_except_emg_raw()
        return

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
    def detect_ttys():
        tty_list = list()

        for p in comports():
            if re.search(r'PID=2458:0*1', p[2]) and p[0] not in tty_list:
                tty_list.append(p[0])
        if len(tty_list) != 2:
            raise ValueError("Two Myo dongles not found!")
        return tty_list[0], tty_list[1]

    def init_myos(self, tty_left=None, tty_right=None, wait_time=10000):
        """
        Connect two myo armbands and recognize left myo and right myo

        :param tty_left: left myo dongle tty name
        :param tty_right: right myo dongle tty name
        :param wait_time: wait time for getting arm type
        :return: left_MyoRaw and right_MyoRaw
        """

        if tty_left is None or tty_right is None:
            tty_left, tty_right = self.detect_ttys()

        if not (self.check_comport(tty_left) and self.check_comport(tty_right)):
            raise ValueError("No comports %s and %s" % (tty_left, tty_right))

        # open arm data switch only
        arm_data_config = MyoConfig()
        arm_data_config.emg_enable = True
        arm_data_config.imu_enable = True

        # CAUTION: ONLY MYO WHOSE MAC ADDRESS IS "cc:25:15:ee:2e:12" IS BE RECOGNISED AS LEFT MYO
        # MYO WHOSE MAC ADDRESS IS "fc:a9:e5:6f:15:6a" IS BE RECOGNISED AS RIGHT MYO

        myo_left = MyoRaw(tty_left, config=arm_data_config, mac_address='cc:25:15:ee:2e:12')
        myo_right = MyoRaw(tty_right, config=arm_data_config, mac_address='fc:a9:e5:6f:15:6a')

        # myo1_arm_type = myo.Arm.UNKNOWN
        # myo2_arm_type = myo.Arm.UNKNOWN
        #
        # # TODO: check why myo cannot send arm data
        #
        # def myo1_arm_type_handler(arm_type, _):
        #     global myo1_arm_type
        #     print(arm_type)
        #     myo1_arm_type = arm_type
        #
        # def myo2_arm_type_handler(arm_type, _):
        #     global myo2_arm_type
        #     print(arm_type)
        #     myo2_arm_type = arm_type
        #
        # myo_left.add_arm_handler(myo1_arm_type_handler)
        # myo_right.add_arm_handler(myo2_arm_type_handler)

        myo_left.connect()
        myo_right.connect()

        # print("Wait for getting arm type......")

        # NEED TO DO SYNC GESTURE TO GET ARM TYPE

        # TODO: Open two threads to get myo data

        # while not(myo1_arm_type != myo.Arm.UNKNOWN and myo2_arm_type != myo.Arm.UNKNOWN):
        #     # if wait_time_now < wait_time:
        #     #     wait_time_now += 1
        #         continue
        #     # else:
        #     #     break
        #
        # print("Get two armbands' arm type")
        #
        # if myo1_arm_type == myo.Arm.LEFT and myo2_arm_type == myo.Arm.RIGHT:
        #     return myo_left, myo_right
        # elif myo1_arm_type == myo.Arm.RIGHT and myo2_arm_type == myo.Arm.LEFT:
        #     return myo_right, myo_left
        #
        return myo_left, myo_right

    def add_left_myo_emg_handler(self, emg_handler):
        if self.left_myo is None or emg_handler is None:
            return
        self.left_myo.add_emg_handler(emg_handler)

    def add_left_myo_imu_handler(self, imu_handler):
        if self.left_myo is None or imu_handler is None:
            return
        self.left_myo.add_imu_handler(imu_handler)

    def add_left_myo_pose_handler(self, pose_handler):
        if self.left_myo is None or pose_handler is None:
            return
        self.left_myo.add_pose_handler(pose_handler)

    def add_left_myo_emg_raw_handler(self, emg_raw_handler):
        if self.left_myo is None or emg_raw_handler is None:
            return
        self.left_myo.add_emg_raw_handler(emg_raw_handler)

    def add_left_myo_arm_handler(self, arm_handler):
        if self.left_myo is None or arm_handler is None:
            return
        self.left_myo.add_arm_handler(arm_handler)

    def add_right_myo_emg_handler(self, emg_handler):
        if self.right_myo is None or emg_handler is None:
            return
        self.right_myo.add_emg_handler(emg_handler)

    def add_right_myo_imu_handler(self, imu_handler):
        if self.right_myo is None or imu_handler is None:
            return
        self.right_myo.add_imu_handler(imu_handler)

    def add_right_myo_pose_handler(self, pose_handler):
        if self.right_myo is None or pose_handler is None:
            return
        self.right_myo.add_pose_handler(pose_handler)

    def add_right_myo_emg_raw_handler(self, emg_raw_handler):
        if self.right_myo is None or emg_raw_handler is None:
            return
        self.right_myo.add_emg_raw_handler(emg_raw_handler)

    def add_right_myo_arm_handler(self, arm_handler):
        if self.right_myo is None or arm_handler is None:
            return
        self.right_myo.add_arm_handler(arm_handler)

    def run(self, timeout=1):
        self.left_myo.run(timeout)
        self.right_myo.run(timeout)

    def disconnect(self):
        self.left_myo.disconnect()
        self.right_myo.disconnect()


if __name__ == '__main__':
    data_queue = queue.Queue()
    lock = multiprocessing.Lock()
    process = MyoDataProcess("myo_process_1", "/dev/ttyACM0", data_queue, lock=lock)
    process1 = MyoDataProcess("myo_process_2", "/dev/ttyACM1", data_queue, lock=lock)
    process.start()
    process1.start()
    process.join()
    process1.join()

