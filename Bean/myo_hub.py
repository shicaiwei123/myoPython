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
import signal

sys.path.append(os.path.abspath(os.path.pardir))

from Bean.myo import MyoRaw
from Bean.myo_config import MyoConfig
from Bean.myo_info import Arm
from serial.tools.list_ports import comports
from Bean.myo_packet import MyoDataPacket, MyoDataType
import redis
import json

logging.basicConfig(level=logging.INFO)
r = redis.Redis(host="127.0.0.1")


class MyoDataProcess(multiprocessing.Process):
    """
    Myo手环进程
    负责判断Myo的手臂类型，之后收集数据，将数据通过queue.Queue传到MyoHub中进行缓存
    """
    class DataHandler(object):
        # 数据回调函数
        def __init__(self, arm_type, emg_data_queue, imu_data_queue):
            self.emg_data_queue = emg_data_queue
            self.imu_data_queue = imu_data_queue
            self.arm_type = arm_type
            self.emg_time = time.time()
        
        def emg_handler(self, emg):
            self.send_data(MyoDataType.EMG, emg)

        def imu_handler(self, quat, acc, gyro):
            self.send_data(MyoDataType.IMU, (quat, acc, gyro))

        def send_data(self, data_type, data):
            # 将数据通过队列发送到Hub
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

        self.myo = MyoRaw(self.serial_port, mac_address=self.mac_addr)
        self.kill_received = False
        self.arm_type = arm_type
        self.open_data = open_data
        self.ready = False
        
        signal.signal(signal.SIGTERM, self.disconnect_myo)
    
    def disconnect_myo(self, signal, signal_state):
        self.myo.disconnect()
        sys.exit(1)
        
    def run(self):
        """
        先连接到手环，然后一直循环拿到数据，直到kill_received标志位为True
        """
        self.connect_myo()
        if self.myo is not None:
            self.init_myo()
        self.logger.info("Start to get myo data")
        while True:
            self.myo.run(1)
        self.logger.info("Process exits")
        
    def config_logger(self, logger_name=__name__):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        return logger

    def connect_myo(self):
        """
        连接手环
        :return:
        """
        self.lock.acquire()
        self.myo.connect(timeout=self.timeout)
        self.myo.never_sleep()
        self.myo.vibrate(1)
        self.lock.release()
    
    def init_myo(self):
        if self.myo is None:
            return
        if self.open_data:
            # 打开数据开关
            self.init_get_data()

    def config_myo(self, arm_enable=True, emg_enable=True, imu_enable=True):
        """
        配置手环
        :param arm_enable:
        :param emg_enable:
        :param imu_enable:
        :return:
        """
        config = MyoConfig()
        config.arm_enable = arm_enable
        config.emg_enable = emg_enable
        config.imu_enable = imu_enable
        self.myo.config_myo(config)

    def init_get_data(self):
        """
        开始获得数据
        """
        # 绑定数据回调函数
        data_handler = self.DataHandler(self.arm_type,
                                        emg_data_queue=self.emg_data_queue,
                                        imu_data_queue=self.imu_data_queue)
        self.myo.add_emg_handler(data_handler.emg_handler)
        self.myo.add_imu_handler(data_handler.imu_handler)
        self.config_myo(arm_enable=False, emg_enable=True, imu_enable=True)
        self.logger.info("Init myo succeed")

    
class MyoHub:

    def __init__(self, myo_num=2):
        
        self.logger = self.config_logger(logger_name="MyoHub")
        self.process_pool = list()  # 进程池
        self.myo_num = myo_num  # 连接数，最大为2
        self.emg_left_pool = multiprocessing.Queue(1)   # 左臂emg数据队列
        self.emg_right_pool = multiprocessing.Queue(1)  # 右臂emg数据队列
        self.imu_left_pool = multiprocessing.Queue(1)   # 左臂imu数据队列
        self.imu_right_pool = multiprocessing.Queue(1)  # 右臂imu数据队列
        self.collect_data_process = None    # 收集数据进程
        self.running = True
        # 手环的mac，必须左臂手环mac地址在前，右臂手环mac在后
        # 由于暂时没能完成通过手环来检测手臂类型的功能，暂时只能指定手环mac
        self.myos_mac = [
            "e6:7a:c5:1e:93:ad",
            # "fc:a9:e5:6f:15:6a",
            "c7:6b:1a:4b:8e:2a",
            # "cc:25:15:ee:2e:12",



        ]
        self.is_reconnecting = False    # 正在重连

    def config_logger(self, logger_name=__name__):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        return logger

    def start(self):
        # 开始
        self.init_myos()
        # self.start_collect_data()

    @staticmethod
    def check_comport(port_name):
        """
        检查是否存在对应名称的蓝牙适配器
        :param port_name: 指定的适配器名称
        :return:
        """
        port_name_list = [p[0] for p in comports()]
        return port_name in port_name_list

    @staticmethod
    def detect_ttys(num=2):
        """
        检测是否存在指定数量的适配器
        :param num: 适配器数量
        :return:
        """
        tty_list = list()

        for p in comports():
            if re.search(r'PID=2458:0*1', p[2]) and p[0] not in tty_list:
                tty_list.append(p[0])
        if len(tty_list) < num:
            raise ValueError("%d Myo dongles not found!" % num)
        return tty_list[0:num]

    def init_myos(self):
        """
        初始化手环及对应的线程
        :return:
        """
        lock = multiprocessing.Lock()
        tty_list = self.detect_ttys(self.myo_num)

        # 根据连接的手环数量创建对应的线程
        for i in range(self.myo_num):
            self.process_pool.append(
                MyoDataProcess(
                    process_name="myo_process_" + str(i+1), # 进程名称
                    serial_port=tty_list.pop(), # 适配器串口
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
            process.start() # 启动进程
    
    def get_data(self, timeout=5):
        """
        收集手环数据
        :param timeout: 超时时间
        :return:
        """
        if self.myo_num == 1:
            # 1个手环
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
            # 两个手环
            t = None if self.is_reconnecting else timeout  # 如果正在重连则不进行超时判断，如果处于正常连接状态则设置超时时间
            try:
                emg_left_data_packet = self.emg_left_pool.get(timeout=t)
                emg_left = emg_left_data_packet.data
                emg_left_timestamp = emg_left_data_packet.timestamp

                imu_left_data_packet = self.imu_left_pool.get(timeout=t)
                imu_left = imu_left_data_packet.data
                imu_left_timestamp = imu_left_data_packet.timestamp

                emg_right_data_packet = self.emg_right_pool.get(timeout=t)
                emg_right = emg_right_data_packet.data
                emg_right_timestamp = emg_right_data_packet.timestamp

                imu_right_data_packet = self.imu_right_pool.get(timeout=t)
                imu_right = imu_right_data_packet.data
                imu_right_timestamp = imu_right_data_packet.timestamp

                self.is_reconnecting = False

                return emg_left, emg_right, imu_left, imu_right
            except queue.Empty:
                # 只要当获取某一个队列的数据超时之后，判断为手环断开，进入重连过程
                self.is_reconnecting = True
                r.publish("log", json.dumps({"type": "mainLog", "data": "检测到手环已断开，正在重连"}))
                # 清空所有数据队列的数据
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
                self.disconnect()
                # 清空进程
                self.process_pool.clear()
                # 重新创建进程
                self.init_myos()
                while not self.is_ready(): continue
                return None, None, None, None

    def is_ready(self):
        """
        检测手环是否已经初始化完成，通过判断数据队列中是否有数据
        如果未初始化完成，则将之前获得的数据都清空
        :return:
        """
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
        """
        断开所有手环的连接，向进程池的所有进程发送terminate信号
        :return:
        """
        self.logger.warning("Send signal to data process")
        for process in self.process_pool:
            process.terminate()
            process.join()
        self.running = False
        while self.collect_data_process is not None and self.collect_data_process.is_alive():
            continue
        self.logger.info("All process has been killed")
    

"""
测试
"""
if __name__ == '__main__':
    hub = MyoHub(myo_num=2)
    hub.start()
    while not hub.is_ready():
        continue
    while True:
        print(hub.get_data())
    logging.error("exit signal")
    hub.disconnect()



