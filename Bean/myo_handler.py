class MyoDefaultHandler:

    def __init__(self):
        pass

    def imu_handler(self, quat, acc, gyro, arm_type=None):
        print(quat, acc, gyro)

    def emg_handler(self, emg, arm_type=None):
        print(emg)

    def emg_raw_handler(self, emg_raw_data, arm_type=None):
        print(emg_raw_data)

    def arm_handler(self, arm, xdir, arm_type=None):
        print(arm, xdir)
