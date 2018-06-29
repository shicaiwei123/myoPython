# coding=utf8
"""
Myo相关信息
"""
import enum


class MyoUUID(enum.Enum):
    IMU = "d5060402-a904-deb9-4748-2c7f4a124842"
    EMG = "d5060104-a904-deb9-4748-2c7f4a124842"
    RAW_EMG1 = "d5060105-a904-deb9-4748-2c7f4a124842"
    RAW_EMG2 = "d5060205-a904-deb9-4748-2c7f4a124842"
    RAW_EMG3 = "d5060305-a904-deb9-4748-2c7f4a124842"
    RAW_EMG4 = "d5060405-a904-deb9-4748-2c7f4a124842"


class MyoService(enum.Enum):
    BATTERY_SERVICE = "0000180f-0000-1000-8000-00805f9b34fb"
    MYO_CONTROL_SERVICE = "d5060001-a904-deb9-4748-2c7f4a124842"
    IMU_SERVICE = "d5060002-a904-deb9-4748-2c7f4a124842"
    ARM_SERVICE = "d5060003-a904-deb9-4748-2c7f4a124842"
    EMG_SERVICE = "d5060004-a904-deb9-4748-2c7f4a124842"
    RAW_EMG_SERVICE = "d5060005-a904-deb9-4748-2c7f4a124842"


class MyoHandler(enum.Enum):
    """
    Myo 不同Handle的值和对应的意义
    CCC 代表对应数据的控制位Handle
    """
    EMG_DATA_HANDLE = 0x27
    EMG_CCC_HANDLE = 0x28
    IMU_DATA_HANDLE = 0x1C
    IMU_CCC_HANDLE = 0x1D
    ARM_DATA_HANDLE = 0x23
    ARM_CCC_HANDLE = 0x24
    COMMAND_INPUT_HANDLE = 0x19
    FIRMWARE_HANDLE = 0x17
    BATTERY_LEVEL_HANDLE = 0x11
    BATTERY_LEVEL_CCC_HANDLE = 0x12
    EMG_RAW_DATA_1_HANDLE = 0X2B
    EMG_RAW_DATA_1_CCC_HANDLE = 0x2C
    EMG_RAW_DATA_2_HANDLE = 0x2E
    EMG_RAW_DATA_2_CCC_HANDLE = 0x2F
    EMG_RAW_DATA_3_HANDLE = 0x31
    EMG_RAW_DATA_3_CCC_HANDLE = 0x32
    EMG_RAW_DATA_4_HANDLE = 0x34
    EMG_RAW_DATA_4_CCC_HANDLE = 0x35


class MyoPose(enum.Enum):
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
    SET_MODE = 1
    VIBRATE = 2
    DEEP_SLEEP = 3
    VIBRATE2 = 4
    SET_SLEEP_MODE = 9
    UNLOCK = 10
    USER_ACTION = 11


class MyoVibrationMode(enum.Enum):
    NONE = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3


class MyoSleepMode(enum.Enum):
    NORMAL = 0
    NEVER_SLEEP = 1


class MyoUnlockMode(enum.Enum):
    LOCK = 0
    LOCK_TIMED = 1
    HOLD = 2


class MyoEmgMode(enum.Enum):
    NONE = 0
    SEND_EMG = 1
    SEND_EMG_RAW = 2


class MyoImuMode(enum.Enum):
    NONE = 0
    SEND_DATA = 1
    SEND_EVENT = 2
    SEND_ALL = 3
    SEND_RAW = 4


class MyoClassifierMode(enum.Enum):
    DISABLED = 0
    ENABLED = 1


class MyoClassifierEventType(enum.Enum):
    ARM_SYNCED = 1
    ARM_UNSYNCED = 2
    POSE = 3
    UNLOCKED = 4
    LOCKED = 5
    SYNC_FAILED = 6


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