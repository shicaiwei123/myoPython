"""
Myo各种功能的Packet类
"""
import enum


class MyoPose(enum.Enum):
    """
    姿态值
    """
    POSE_REST = 0
    POSE_FIST = 1
    POSE_WAVE_IN = 2
    POSE_WAVE_OUT = 3
    POSE_FINGERS_SPREAD = 4
    POSE_DOUBLE_TAP = 5


class MyoMKU(enum.Enum):
    BLACK_MYO = 1
    WHITE_MYO = 2


class MyoCommand(enum.Enum):
    """
    各种命令的值及含义
    """
    SET_MODE = 1
    VIBRATE = 3
    DEEP_SLEEP = 4
    VIBRATE2 = 7
    SET_SLEEP_MODE = 9
    UNLOCK = 10
    USER_ACTION = 11


class MyoVibrationMode(enum.Enum):
    """
    震动时长
    """
    NONE = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3


class MyoSleepMode(enum.Enum):
    """
    睡眠模式
    """
    NORMAL = 0
    NEVER_SLEEP = 1


class MyoUnlockMode(enum.Enum):
    """
    锁定模式
    """
    LOCK = 0
    LOCK_TIMED = 1
    HOLD = 2


class MyoDataType(enum.Enum):
    """
    发送的数据类型
    """
    EMG = 0
    IMU = 1


class MyoCommandHeader:
    """
    Myo专有的指令头部
    """
    def __init__(self, command, payload_size):
        """
        :param command: 命令类型，参考MyoCommand
        :param payload_size:
        """
        self.command = command
        self.len = payload_size


class MyoWriteAttrCommandPacket:
    def __init__(self, header: MyoCommandHeader, attr_handle: int, len: int, payload):
        """
        写Handle指令
        :param header: MyoCommandHeader,命令头部
        :param attr_handle: 目标Handle
        :param len: 整个命令数据包的长度
        :param payload: 数据
        """
        self.header = header
        self.attr_handle = attr_handle
        self.len = len
        self.payload = payload


class MyoReadAttrCommandPacket:
    def __init__(self, header: MyoCommandHeader, attr_handle: int):
        """
        读Handle指令
        :param header: 命令头部
        :param attr_handle: 目标Handle
        """
        self.header = header
        self.attr_handle = attr_handle


class MyoVibrateCommandPacket:
    """
    震动命令
    """
    def __init__(self, header: MyoCommandHeader, vibrate_type):
        self.header = header
        self.vibrate_type = vibrate_type

    def get_bytes(self):
        return bytes.fromhex(("{:02X}" * (self.header.len + 2)).format(
            self.header.command,
            self.header.len,
            self.vibrate_type))


class MyoDeepSleepCommandPacket:
    """
    深度休眠指令，即关机指令
    """

    def __init__(self, header: MyoCommandHeader):
        self.header = header

    def get_bytes(self):
        return bytes.fromhex(
            ("{:02X}" * (self.header.len + 2)).format(
                self.header.command,
                self.header.len
            )
        )


class MyoSetSleepCommandPacket:
    """
    设置睡眠模式指令
    """

    def __init__(self, header: MyoCommandHeader, sleep_mode):
        self.header = header
        self.sleep_mode = sleep_mode

    def get_bytes(self):
        return bytes.fromhex(
            ("{:02X}" * (self.header.len + 2)).format(
                self.header.command,
                self.header.len,
                self.sleep_mode
            )
        )


class MyoUnlockCommandPacket:
    """
    解锁指令
    """
    def __init__(self, header: MyoCommandHeader, unlock_type):
        self.header = header
        self.type = unlock_type

    def get_bytes(self):
        return bytes.fromhex(
            ("{:02X}" * (self.header.len + 2)).format(
                self.header.command,
                self.header.len,
                self.type
            )
        )


class MyoDataPacket:
    """
    发送给Hub处理的数据包
    """
    def __init__(self, arm_type, data_type: MyoDataType, data, timestamp=None):
        """
        :param arm_type: 手臂类型，参考Arm类
        :param data_type: 数据类型，参考MyoDataType
        :param data: 数据
        :param timestamp: 时间戳
        """
        self.arm_type = arm_type
        self.data_type = data_type
        self.data = data
        self.timestamp = timestamp
