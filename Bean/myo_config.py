class MyoConfig:

    def __init__(self):
        self.emg_enable = False
        self.imu_enable = False
        self.arm_enable = False
        self.emg_raw_enable = False

    def open_all_except_emg_raw(self):
        self.emg_enable = True
        self.imu_enable = True
        self.arm_enable = True
        self.emg_raw_enable = False

    def open_all(self):
        self.emg_enable = True
        self.imu_enable = True
        self.arm_enable = True
        self.emg_raw_enable = True