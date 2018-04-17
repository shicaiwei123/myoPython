# coding=utf8
"""
Myo相关定义类
"""

from bluepy import btle

from Bean.myo_packet import *
from Bean.myo_utils import *


class Arm(enum.Enum):
    UNKNOWN = 0
    RIGHT = 1
    LEFT = 2


class XDirection(enum.Enum):
    UNKNOWN = 0
    X_TOWARD_WRIST = 1
    X_TOWARD_ELBOW = 2


class Pose(enum.Enum):
    REST = 0
    FIST = 1
    WAVE_IN = 2
    WAVE_OUT = 3
    FINGERS_SPREAD = 4
    THUMB_TO_PINKY = 5
    UNKNOWN = 255


class MyoUUID(enum.Enum):
    IMU = "d5060402-a904-deb9-4748-2c7f4a124842"
    EMG = "d5060104-a904-deb9-4748-2c7f4a124842"
    RAW_EMG1 = "d5060105-a904-deb9-4748-2c7f4a124842"
    RAW_EMG2 = "d5060205-a904-deb9-4748-2c7f4a124842"
    RAW_EMG3 = "d5060305-a904-deb9-4748-2c7f4a124842"
    RAW_EMG4 = "d5060405-a904-deb9-4748-2c7f4a124842"


class MyoRaw(object):
    """Implements the Myo-specific communication protocol."""

    def __init__(self, mac_addr, config=None):
        """
        :param tty: 串口实例
        :param config: Myo配置文件，应传入myo_config实例
        :param both: if connect two myos
        """
        self.config = config
        self.myo = None

        self.emg_handlers = []
        self.imu_handlers = []
        self.arm_handlers = []
        self.pose_handlers = []
        self.emg_raw_handlers = []
        self.mac_addr = mac_addr
        self.status = None
        self.arm_type = None

    def connect(self, init_delegate, iface=0):

        # def data_handle(handle, data):
        #     if handle == MyoHandler.EMG_DATA_HANDLE.value:
        #         vals = unpack('8HB', data)
        #         emg = vals[:8]
        #         self.on_emg(emg, self.arm_type)
        #
        #     if handle == MyoHandler.IMU_DATA_HANDLE.value:
        #         vals = unpack('10h', data)
        #         quat = vals[:4]
        #         acc = vals[4:7]
        #         gyro = vals[7:10]
        #         self.on_imu(quat, acc, gyro, self.arm_type)
        #
        #     if handle == MyoHandler.ARM_DATA_HANDLE.value:
        #         typ, val, xdir, pose, sync_result = unpack('3BHB', data)
        #
        #         if typ == MyoClassifierEventType.ARM_SYNCED.value:
        #             self.on_arm(Arm(val), XDirection(xdir))
        #         elif typ == MyoClassifierEventType.ARM_UNSYNCED.value:  # removed from arm
        #             self.on_arm(Arm.UNKNOWN, XDirection.UNKNOWN)
        #         elif typ == MyoClassifierEventType.POSE.value:  # pose
        #             self.on_pose(Pose(val))
        #
        #     print(handle, data)

        if not isinstance(iface, int):
            return

        if self.myo is None:
            self.myo = btle.Peripheral(self.mac_addr, iface=iface)
        self.myo.withDelegate(init_delegate)
        self.never_sleep()
        self.set_lock(MyoUnlockMode.HOLD)
        self.config_myo(self.config)

    def disconnect(self):
        self.normal_sleep()
        self.set_lock(MyoUnlockMode.LOCK_TIMED)
        if self.myo is not None:
            self.myo.disconnect()

    def config_myo(self, myo_config):
        """
        如果沒有配置文件则默认开启emg数据通道
        :param myo_config:
        :return:
        """
        if myo_config is None:
            return

        if myo_config.emg_enable:
            self.is_broadcast_data(MyoHandler.EMG_CCC_HANDLE, True)
        elif myo_config.emg_raw_enable:
            self.is_broadcast_data(MyoHandler.EMG_RAW_DATA_1_CCC_HANDLE, True)
            self.is_broadcast_data(MyoHandler.EMG_RAW_DATA_2_CCC_HANDLE, True)
            self.is_broadcast_data(MyoHandler.EMG_RAW_DATA_3_CCC_HANDLE, True)
            self.is_broadcast_data(MyoHandler.EMG_RAW_DATA_4_CCC_HANDLE, True)

        if myo_config.imu_enable:
            self.is_broadcast_data(MyoHandler.IMU_CCC_HANDLE, True)

        if myo_config.classifier_enable:
            # 使能arm数据通知
            self.is_broadcast_data(MyoHandler.ARM_CCC_HANDLE, True)

        self.enable_data(emg_enable=myo_config.emg_enable,
                         imu_enable=myo_config.imu_enable,
                         classifier_enable=myo_config.classifier_enable,
                         emg_raw_enable=myo_config.emg_raw_enable)

    def run(self, timeout=1.0):
        if self.myo is not None:
            self.myo.waitForNotifications(timeout)

    def vibrate(self, mode: MyoVibrationMode):
        command = MyoVibrateCommandPacket(
            header=MyoCommandHeader(
                command=MyoCommand.VIBRATE,
                payload_size=1
            ),
            vibrate_type=mode
        )
        self.write_command(command.get_bytes())

    def normal_sleep(self):
        command = MyoSetSleepCommandPacket(
            header=MyoCommandHeader(
                command=MyoCommand.SET_SLEEP_MODE,
                payload_size=1
            ),
            sleep_mode=MyoSleepMode.NORMAL
        )
        self.write_command(command.get_bytes())

    def never_sleep(self):
        command = MyoSetSleepCommandPacket(
            header=MyoCommandHeader(
                command=MyoCommand.SET_SLEEP_MODE,
                payload_size=1
            ),
            sleep_mode=MyoSleepMode.NEVER_SLEEP
        )
        self.write_command(command.get_bytes())

    def set_lock(self, lock_type: MyoUnlockMode):
        """
        configure lock status
        :param conn: connection
        :param lock_type: lock type in MyoUnlockMode
        :return:
        """
        command = MyoUnlockCommandPacket(
            header=MyoCommandHeader(
                command=MyoCommand.UNLOCK,
                payload_size=1
            ),
            unlock_type=lock_type
        )
        self.write_command(command.get_bytes())

    def get_battery_level(self):
        return self.read_char(MyoHandler.BATTERY_LEVEL_HANDLE)

    def is_broadcast_data(self, handle: MyoHandler, enable):
        """
        使能或关闭数据广播
        :param handle: 数据对应的CCC的handle
        :param enable: True or False
        :return:
        """
        if enable:
            # arm data need to write b'\x02\x00' to open, not b'\x01\x00'\
            # 写入命令让Myo广播对应的数据
            if handle == MyoHandler.ARM_CCC_HANDLE:
                self.write_char(handle, b'\x02\x00')
            else:
                self.write_char(handle, b'\x01\x00')
        else:
            self.write_char(handle, b'\x00\x00')

    def enable_data(self,
                    emg_enable=False,
                    imu_enable=False,
                    classifier_enable=False,
                    emg_raw_enable=False):
        """
        打开或关闭数据开关
        :param emg_enable: 使能emg数据
        :param imu_enable: 使能imu数据
        :param classifier_enable: 使能arm数据
        :param emg_raw_enable: 使能raw数据
        :return:
        """
        if emg_enable:
            emg_mode = MyoEmgMode.SEND_EMG
        elif emg_raw_enable:
            emg_mode = MyoEmgMode.SEND_EMG_RAW
        else:
            emg_mode = MyoEmgMode.NONE

        if imu_enable:
            imu_mode = MyoImuMode.SEND_DATA
        else:
            imu_mode = MyoImuMode.NONE

        if classifier_enable:
            classifier_mode = MyoClassifierMode.ENABLED
        else:
            classifier_mode = MyoClassifierMode.DISABLED

        command = MyoDataEnableCommandPacket(
            header=MyoCommandHeader(
                command=MyoCommand.SET_MODE,
                payload_size=3
            ),
            emg_mode=emg_mode,
            imu_mode=imu_mode,
            classifier_mode=classifier_mode
        )

        self.write_command(command.get_bytes())

    def write_command(self, command):
        self.write_char(MyoHandler.COMMAND_INPUT_HANDLE, command)

    def write_char(self, handle: MyoHandler, data):
        if self.myo is None:
            return
        self.myo.writeCharacteristic(handle.value, data)

    def read_char(self, handle: MyoHandler):
        if self.myo is None:
            return None
        return self.myo.readCharacteristic(handle.value)

    def replace_delegate(self, delegate):
        self.myo.withDelegate(delegate)

    def get_firmware_version(self):
        data = self.read_char(MyoHandler.FIRMWARE_HANDLE)
        _, _, _, _, v0, v1, v2, v3 = unpack('BHBBHHHH', data)
        return v0, v1, v2, v3

    def get_name(self):
        return self.read_char(0x03)

    def add_emg_handler(self, h):
        self.emg_handlers.append(h)

    def remove_emg_handler(self, h):
        self.emg_handlers.remove(h)

    def add_imu_handler(self, h):
        self.imu_handlers.append(h)

    def remove_imu_handler(self, h):
        self.imu_handlers.remove(h)

    def add_pose_handler(self, h):
        self.pose_handlers.append(h)

    def remove_pose_handler(self, h):
        self.pose_handlers.remove(h)

    def add_arm_handler(self, h):
        self.arm_handlers.append(h)

    def remove_arm_handler(self, h):
        self.arm_handlers.remove(h)

    def add_emg_raw_handler(self, h):
        self.emg_raw_handlers.append(h)

    def remove_emg_raw_handler(self, h):
        self.emg_raw_handlers.remove(h)

    def on_emg(self, emg, arm_type=None):
        for h in self.emg_handlers:
            h(emg, arm_type)

    def on_imu(self, quat, acc, gyro, arm_type=None):
        for h in self.imu_handlers:
            h(quat, acc, gyro, arm_type)

    def on_pose(self, p):
        for h in self.pose_handlers:
            h(p)

    def on_arm(self, arm, xdir):
        for h in self.arm_handlers:
            h(arm, xdir)

    def on_emg_raw(self, data):
        # index: emg sensor index
        # 对数据进行矫正
        data = self.process_emg_raw_data(data)
        for h in self.emg_raw_handlers:
            h(data)

    def process_emg_raw_data(self, data):
        return tuple([x if x <= 128 else x - 256 for x in data])
