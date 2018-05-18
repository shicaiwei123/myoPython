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
import threading

sys.path.append(os.path.abspath(os.path.pardir))

from Bean.myo import MyoRaw
from Bean.myo_config import MyoConfig
from Bean.myo_info import Arm
from serial.tools.list_ports import comports
from Bean.myo_packet import MyoDataPacket, MyoDataType

class MyoDataProcess(multiprocessing.Process):
    """
    负责判断Myo的手臂类型，之后收集数据，将数据通过queue.Queue传到MyoHub中进行缓存
    """
    class ArmHandler(object):
        def __init__(self):
            self.arm_type = Arm.UNKNOWN
        
        def arm_handler(self, arm, xdir):
            self.arm_type = arm
    
    class DataHandler(object):
        def __init__(self, arm_type, emg_data_queue, imu_data_queue):
            self.emg_data_queue = emg_data_queue
            self.imu_data_queue = imu_data_queue
            self.arm_type = arm_type
            self.emg_time = time.time()
        
        def emg_handelr(self, emg):
            self.send_data(MyoDataType.EMG, emg)

        def imu_handler(self, quat, acc, gyro):
            self.send_data(MyoDataType.IMU, (acc, gyro))

        def send_data(self, data_type, data):
            data_packet = MyoDataPacket(
                self.arm_type,
                data_type=data_type,
                data=data,
                timestamp=time.time()
            )
            if data_type == MyoDataType.EMG:
                self.emg_time = time.time()
                try:
                    self.emg_data_queue.put_nowait(data_packet)
                except queue.Full:
                    pass
            elif data_type == MyoDataType.IMU:
                try:
                    self.imu_data_queue.put_nowait(data_packet)
                except queue.Full:
                    pass

    def __init__(self, process_name, serial_port, emg_data_queue, imu_data_queue, lock, timeout=30, mac_addr="", open_data=True, arm_type=Arm.UNKNOWN):
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

        self.emg_data_queue = emg_data_queue
        self.imu_data_queue = imu_data_queue

        self.timeout = timeout
        self.serial_port = serial_port
        self.mac_addr = mac_addr

        self.myo = None

        self.kill_received = False
        self.arm_type = arm_type
        self.open_data = open_data
        self.ready = False

    def run(self):
        """
        先连接到手环，然后一直循环，直到kill_received标志位为True
        """
        if self.myo is None:
            self.connect_myo()
        if self.myo is not None:
            self.init_myo()
        self.logger.info("Start to get myo data")
        while not self.kill_received:
            #self.lock.acquire()
            self.myo.run(1)
            #self.lock.release()
        self.logger.info("Process exits")
        self.disconnect_myo()
        
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
            self.myo.never_sleep()
            self.myo.vibrate(1)
            self.lock.release()
        except TimeoutError as e:
            self.myo = None
            self.logger.error("Cannot connect myo through %s, %s exit", self.serial_port, self.process_name)

    def disconnect_myo(self):
        self.myo.disconnect()
    
    def init_myo(self, open_data=True):
        if self.myo is None:
            return
        # self.get_myo_arm_type()
        # if self.arm_type == Arm.UNKNOWN:
        #     return
        # 打开Myo数据开关
        if self.open_data:
            self.init_get_data()
        

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
            self.lock.acquire()
            self.myo.run(1)
            self.lock.release()
        if myo_arm_handler.arm_type == Arm.UNKNOWN:
            self.logger.warning("Waiting for myo timeout!")
        else:
            self.arm_type = myo_arm_handler.arm_type
            self.logger.info("Get myo arm type: %s", myo_arm_handler.arm_type)

    def init_get_data(self):
        """
        开始获得数据
        """
        data_handler = self.DataHandler(self.arm_type,
                                        emg_data_queue=self.emg_data_queue,
                                        imu_data_queue=self.imu_data_queue)
        self.myo.add_emg_handler(data_handler.emg_handelr)
        self.myo.add_imu_handler(data_handler.imu_handler)
        self.config_myo(arm_enable=False, emg_enable=True, imu_enable=True)
        self.ready = True
        # # 通过emg的数据通道判断是否同步
        # self.emg_data_queue.put(self.ready)
        self.logger.info("Init myo succeed")

    
class MyoHub:

    def __init__(self, myo_num=2, tty_one=None, tty_two=None):
        
        self.logger = self.config_logger(logger_name="MyoHub")
        self.process_pool = list()
        self.queue_pool = list()
        self.myo_num = myo_num
        self.emg_left_pool = multiprocessing.Queue(1)
        self.emg_right_pool = multiprocessing.Queue(1)
        self.imu_left_pool = multiprocessing.Queue(1)
        self.imu_right_pool = multiprocessing.Queue(1)
        self.collect_data_process = None
        self.running = True
        self.myos_mac = [
            # "e6:7a:c5:1e:93:ad",
            "fc:a9:e5:6f:15:6a",
            # "c7:6b:1a:4b:8e:2a",
            "cc:25:15:ee:2e:12",



        ]
        self.drop_num = 2
        self.is_droped = False

    def config_logger(self, logger_name=__name__):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        return logger

    def start(self):
        self.init_myos()
        # self.start_collect_data()

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
    def detect_ttys(num=2):
        tty_list = list()

        for p in comports():
            if re.search(r'PID=2458:0*1', p[2]) and p[0] not in tty_list:
                tty_list.append(p[0])
        if len(tty_list) < num:
            raise ValueError("%d Myo dongles not found!" % num)
        return tty_list[0:num]

    def init_myos(self, wait_time=10000):

        lock = multiprocessing.Lock()
        tty_list = self.detect_ttys(self.myo_num)

        for i in range(self.myo_num):
            self.process_pool.append(
                MyoDataProcess(
                    process_name="myo_process_" + str(i+1),
                    serial_port=tty_list.pop(),
                    emg_data_queue=self.emg_left_pool if i % 2 == 0 else self.emg_right_pool,
                    imu_data_queue=self.imu_left_pool if i % 2 == 0 else self.imu_right_pool,
                    lock = lock,
                    open_data=True,
                    arm_type=Arm.LEFT if i % 2 == 0 else Arm.RIGHT,
                    mac_addr=self.myos_mac[i]
                )
            )
        for process in self.process_pool:
            process.daemon = True
            process.start()
    
    # def start_collect_data(self):
    #     while not self.is_ready():
    #         continue
    #     self.ready = True
    #     self.collect_data_process = multiprocessing.Process(target=self.collect_data, args=(
    #         self.myo_num, self.queue_pool, self.emg_left_pool, self.emg_right_pool, self.imu_left_pool, self.imu_right_pool,))
    #     self.collect_data_process.daemon = True
    #     self.collect_data_process.start()
    #
    # # 丢弃
    # def collect_data(self, myo_num, data_pool, emg_left_pool, emg_right_pool, imu_left_pool, imu_right_pool):
    #     while self.running:
    #         if not self.ready:
    #             continue
    #         for data_queue in data_pool:
    #             try:
    #                 data = data_queue.get_nowait()
    #                 if data.arm_type == Arm.LEFT and data.data_type == MyoDataType.EMG:
    #                     print(data.arm_type, data.data, time.time())
    #                 if data.data_type == MyoDataType.EMG:
    #                     if myo_num == 1 or data.arm_type == Arm.LEFT:
    #                         emg_left_pool.put(data.data)
    #                         continue
    #                     elif data.arm_type == Arm.RIGHT:
    #                         emg_right_pool.put(data.data)
    #                         continue
    #                 elif data.data_type == MyoDataType.IMU:
    #                     if myo_num == 1 or data.arm_type == Arm.LEFT:
    #                         imu_left_pool.put(data.data)
    #                         continue
    #                     if data.arm_type == Arm.RIGHT:
    #                         imu_right_pool.put(data.data)
    #                         continue
    #             except queue.Empty as e:
    #                 continue
    
    def get_data(self):
        if self.myo_num == 1:
            try:
                emg_left = self.emg_left_pool.get_nowait()
            except queue.Empty as e:
                emg_left = None
            try:
                imu_left = self.imu_left_pool.get_nowait()
            except queue.Empty as e:
                imu_left = None
            return emg_left, imu_left
        elif self.myo_num == 2:

            # 首先丢弃@self.drop_num次imu数据，使数据同步
            emg_left_data_packet = self.emg_left_pool.get()
            emg_left = emg_left_data_packet.data
            emg_left_timestamp = emg_left_data_packet.timestamp

            # if not self.is_droped:
            #     for i in range(self.drop_num):
            #         imu_left_data_packet = self.imu_left_pool.get()
            #         imu_left = imu_left_data_packet.data
            #         imu_left_timestamp = imu_left_data_packet.timestamp
            # else:
            imu_left_data_packet = self.imu_left_pool.get()
            imu_left = imu_left_data_packet.data
            imu_left_timestamp = imu_left_data_packet.timestamp

            emg_right_data_packet = self.emg_right_pool.get()
            emg_right = emg_right_data_packet.data
            emg_right_timestamp = emg_right_data_packet.timestamp

            # if not self.is_droped:
            #     for i in range(self.drop_num):
            #         imu_right_data_packet = self.imu_right_pool.get()
            #         imu_right = imu_right_data_packet.data
            #         imu_right_timestamp = imu_right_data_packet.timestamp
            # else:
            imu_right_data_packet = self.imu_right_pool.get()
            imu_right = imu_right_data_packet.data
            imu_right_timestamp = imu_right_data_packet.timestamp

            self.is_droped = True

            return emg_left, emg_right, imu_left, imu_right
            # return emg_left_timestamp, emg_right_timestamp, imu_left_timestamp, imu_right_timestamp, emg_left_timestamp - imu_left_timestamp, emg_right_timestamp - imu_right_timestamp
            # return 0.0, 0.0, 0.0, 0.0

    def is_ready(self):

        try:
            self.emg_right_pool.get_nowait()
        except queue.Empty:
            while True:
                try:
                    self.emg_left_pool.get_nowait()
                except queue.Empty:
                    break
            while True:
                try:
                    self.imu_left_pool.get_nowait()
                except queue.Empty:
                    break
            while True:
                try:
                    self.imu_right_pool.get_nowait()
                except queue.Empty:
                    break
            return False
        return True

    def disconnect(self):
        self.logger.warning("Send signal to data process")
        for process in self.process_pool:
            process.kill_received = True
        for process in self.process_pool:
            while process.is_alive():
                continue
        self.running = False
        while self.collect_data_process.is_alive():
            continue
        self.logger.info("All process has been killed")
    

if __name__ == '__main__':
    hub = MyoHub(myo_num=2)
    hub.start()
    while not hub.is_ready():
        continue
    # time.sleep(1)
    while True:
        data = hub.get_data()
        print("%.4f, %.4f, %.4f, %.4f, %.4f, %.4f" % data)

