import logging
import multiprocessing
import queue
import threading
import sys
import os

sys.path.append(os.path.abspath(os.path.pardir))

from Bean.myo_hub import MyoStatus, MyoHub


def get_hub_data(myo_hub):
    myo_hub.get_data()


class MyoMonitorProcess(multiprocessing.Process):

    def __init__(self, myo_count):
        multiprocessing.Process.__init__(self)
        self.myo_hub = MyoHub(myo_count=myo_count)
        self.myo_count = myo_count
        self.myo_hub_data_thread = threading.Thread(target=get_hub_data, args=(self.myo_hub,))

        self.kill_received = False
        self.kill_all_data_thread_flag = False
        self.logger = logging.getLogger("myo")

    def run(self):
        if not self.myo_hub.running:
            self.myo_hub.run()
            self.myo_hub_data_thread.start()

    def kill_all_data_thread(self):
        self.logger.info("start to kill all myo data thread")
        for thread in self.myo_hub.myo_thread_pool:
            thread.kill_received = True
        self.kill_all_data_thread_flag = True
        self.logger.info("waiting for thread exit...")

    def disconnect(self):
        self.myo_hub.disconnect()

    def get_data(self):
        try:
            if self.myo_count == 1:
                return self.myo_hub.emg_queue.get(), self.myo_hub.imu_queue.get()
            elif self.myo_count == 2:
                return self.myo_hub.emg_left_queue.get(), self.myo_hub.imu_left_queue.get(), self.myo_hub.emg_right_queue.get(), self.myo_hub.imu_right_queue.get()
        except queue.Empty as e:
            return None, None


if __name__ == '__main__':
    process = MyoMonitorProcess(1)
    process.run()
    while True:
        print(process.get_data())




