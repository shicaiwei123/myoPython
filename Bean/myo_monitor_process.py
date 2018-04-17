import logging
import multiprocessing
import queue

from Bean.myo import Arm
from Bean.myo_handler import MyoDefaultHandler
from Bean.myo_hub import MyoStatus, MyoHub


class MyoMonitorHandler(MyoDefaultHandler):

    def __init__(self):
        super().__init__()
        self.emg_left_queue = queue.Queue()
        self.emg_right_queue = queue.Queue()
        self.imu_left_queue = queue.Queue()
        self.imu_right_queue = queue.Queue()
        self.emg_raw_left_queue = queue.Queue()
        self.emg_raw_right_queue = queue.Queue()

    def emg_handler(self, emg, arm_type=None):
        if arm_type == Arm.LEFT:
            self.emg_left_queue.put(emg)
        elif arm_type == Arm.RIGHT:
            self.emg_right_queue.put(emg)

    def imu_handler(self, quat, acc, gyro, arm_type=None):
        if arm_type == Arm.LEFT:
            self.imu_left_queue.put((quat, acc, gyro))
        elif arm_type == Arm.RIGHT:
            self.imu_right_queue.put((quat, acc, gyro))

    def emg_raw_handler(self, emg_raw_data, arm_type=None):
        if arm_type == Arm.LEFT:
            self.emg_raw_left_queue.put(emg_raw_data)
        elif arm_type == Arm.RIGHT:
            self.emg_raw_right_queue.put(emg_raw_data)


class MyoMonitorProcess(multiprocessing.Process):

    def __init__(self, myo_count):
        multiprocessing.Process.__init__(self)
        self.monitor_handler = MyoMonitorHandler()
        self.myo_hub = MyoHub(myo_count=myo_count, handler=self.monitor_handler)
        self.myo_count = myo_count

        self.kill_received = False
        self.kill_all_data_thread_flag = False
        self.logger = logging.getLogger("myo")

    def run(self):
        while not self.kill_received:
            if not self.myo_hub.running:
                self.myo_hub.run()

            while not self.kill_all_data_thread_flag:
                for thread in self.myo_hub.myo_thread_pool:
                    if thread.status == MyoStatus.DISCONNECTED:
                        self.kill_all_data_thread()
            self.logger.info("myo disconnected, start to scan %s myos" % self.myo_count)
            self.myo_hub.myo_thread_pool = []

            while len(self.myo_hub.myo_thread_pool) != self.myo_count:
                self.logger.info("continue scanning...")
                self.myo_hub.scan_myos(self.myo_count)

        self.logger.info("kill signal received, waiting for thread exit...")
        self.myo_hub.disconnect()

    def kill_all_data_thread(self):
        self.logger.info("start to kill all myo data thread")
        for thread in self.myo_hub.myo_thread_pool:
            thread.kill_received = True
        self.kill_all_data_thread_flag = True
        self.logger.info("waiting for thread exit...")

    def get_data(self):
        return



