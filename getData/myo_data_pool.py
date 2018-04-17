import queue
import threading
import time

import numpy as np

from Bean.myo import MyoRaw
from Bean.myo_config import MyoConfig


class DataPool:
    """
    获得Myo的各种数据
    """
    # handlers列表
    handlers = []

    def __init__(self, timeout=0):
        """
        数据池初始化
        :param timeout: get超时时间
        """
        # 生成配置信息，打开Myo的开关
        config = MyoConfig()
        config.emg_raw_enable = True
        config.imu_enable = True
        config.emg_enable = True
        config.classifier_enable = True

        self.myo = MyoRaw(config=config)
        # 连接Myo

        # emg
        self.emg_queue = queue.Queue()
        # 加速度值
        self.acc_queue = queue.Queue()
        # 角度值
        self.angle_queue = queue.Queue()
        # 陀螺仪值
        self.gyro_queue = queue.Queue()
        # emg_raw
        self.emg_raw_queue = queue.Queue()

        self.timeout = timeout
        # run time
        self.run_time = 0

        self.myo_data_thread = None
        self.monitor_thread = None

    def __get_queue_data(self, data_queue):
        """
        Get Different Specific Type of Data from data_queue
        :param data_queue:
        :return: Data or None
        """
        try:
            data = data_queue.get(timeout=self.timeout)
            return data
        except queue.Empty:
            return None

    def get_emg_raw_data(self):
        return self.__get_queue_data(self.emg_raw_queue)

    def get_emg_data(self):
        """
        Get EMG data
        :return: (emg1, emg2, emg3, emg4, emg5, emg6, emg7, emg8, timestamp)
        """
        return self.__get_queue_data(self.emg_queue)

    def get_acc_data(self):
        """
        获取加速度数据
        :return:(acc1, acc2, acc3, timestamp)
        """
        # acc数据形式
        return self.__get_queue_data(self.acc_queue)

    def get_gyro_data(self):
        """
        获取陀螺仪数据
        :return: tuple or None
        """
        # gyro数据形式
        # (gyro1, gyro2, gyro3, time)
        return self.__get_queue_data(self.gyro_queue)

    def get_angle_data(self):
        """
        获取计算后的角度数据
        :return:
        """
        # 数据形式
        # (roll, pitch, yaw)
        return self.__get_queue_data(self.angle_queue)

    def start(self):
        """
        将myo的数据传入queue中
        """
        self.__start_get_data_thread()
        # self.__start_monitor_thread()

    def __start_get_data_thread(self):
        if self.myo_data_thread is None:
            self.myo_data_thread = GetDataThread(self.myo,
                                                 self.emg_queue,
                                                 self.emg_raw_queue,
                                                 self.acc_queue,
                                                 self.gyro_queue,
                                                 self.angle_queue)
        if not self.myo_data_thread.is_alive():
            # start time
            self.run_time = time.time()
            self.myo_data_thread.start()

    def __start_monitor_thread(self):

        queue_dict = {"emg_queue": self.emg_queue,
                      "acc_queue": self.acc_queue,
                      "angle_queue": self.angle_queue,
                      "gyro_queue": self.gyro_queue}

        if self.monitor_thread is None:
            self.monitor_thread = MonitorThread(queue_dict)
        if not self.monitor_thread.is_alive():
            self.monitor_thread.start()


class MonitorThread(threading.Thread):
    """
    监控各个队列数目进程
    """

    def __init__(self, queues):
        """
        初始化
        :param queues: queue字典
        """
        threading.Thread.__init__(self)
        self.queues = queues

    def run(self):
        """
        实时打印各queue的数据数量
        :return:
        """
        while True:
            try:
                for key, value in self.queues.items():
                    print("%s: %d" % (key, value.qsize()))
                print()
            except Exception as e:
                print(e)
                break


class GetDataThread(threading.Thread):

    def __init__(self, myo,
                 emg_queue, emg_raw_queue, acc_queue, gyro_queue, angle_queue,
                 window_size=5):
        threading.Thread.__init__(self)
        # 临时数据缓存
        self.myo = myo
        self.emg_queue = emg_queue
        self.acc_queue = acc_queue
        self.gyro_queue = gyro_queue
        self.angle_queue = angle_queue
        self.emg_raw_queue = emg_raw_queue

        self.window_size = window_size

        self.emg_temp = list()
        self.acc_temp = list()
        self.gyro_temp = list()

    def run(self):

        self.myo.add_emg_raw_handler(self.emg_raw_handler)
        self.myo.add_imu_handler(self.imu_handler)
        self.myo.add_emg_handler(self.emg_handler)
        self.myo.connect()

        while True:
            # 一直运行
            try:
                self.myo.run(1)
            except Exception as e:
                print(e)
                print("GetData thread exit!")
                break

    def emg_raw_handler(self, emg_raw):
        data = self.__process_emg_raw_data(list(emg_raw))
        data.append(time.time())
        self.emg_raw_queue.put(data)

    def emg_handler(self, emg):
        temp = [x / 100 for x in emg]
        temp.append(time.time())
        self.emg_queue.put(temp)

        # self.emg_temp.append(emg)
        #
        # if len(self.emg_temp) == self.window_size:
        #     self.emg_queue.put(list(emg))
        #     self.emg_temp.clear()

    def imu_handler(self, quat, acc, gyro):
        # roll, pitch, yaw = self.__calc_angular(quat)
        # self.angle_queue.put([roll, pitch, yaw])

        # self.acc_temp.append(acc)
        # self.gyro_temp.append(gyro)
        #
        # if len(self.acc_temp) == self.window_size:
        #     self.acc_queue.put(list(acc))
        #     self.acc_temp.clear()
        # if len(self.gyro_temp) == self.window_size:
        #     self.gyro_queue.put(list(gyro))
        #     self.gyro_temp.clear()
        acc_data = list(acc)
        acc_data.extend(time.time())
        self.acc_queue.put(acc_data)

        # self.gyro_queue.put(gyro)

    def __calc_angular(self, orientation_data):
        """
        通过四元数计算角度
        :param orientation_data: 四元数数据
        :return:
        """
        x = orientation_data[0]
        y = orientation_data[1]
        z = orientation_data[2]
        w = orientation_data[3]
        # 滚转角 x轴
        roll = np.arctan2(2.0 * (w * x + y * z),
                          1.0 - 2.0 * (x * x + y * y))
        # 俯仰角 y轴
        pitch = np.arcsin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
        # 偏航角 z轴
        yaw = np.arctan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
        return roll, pitch, yaw

    def __process_emg_raw_data(self, data):
        """
        process emg raw data, data from (0, 256)] will change to (-128, 128)
        :param data: emg_raw_data
        :return:
        """
        return [item if item < 128 else item - 256 for item in data]
