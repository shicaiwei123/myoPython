# coding=utf8
"""
Myo相关信息
"""
import enum


class MyoUUID(enum.Enum):
    """
    各个Handle的UUID
    """
    IMU = "d5060402-a904-deb9-4748-2c7f4a124842"
    EMG = "d5060104-a904-deb9-4748-2c7f4a124842"
    RAW_EMG1 = "d5060105-a904-deb9-4748-2c7f4a124842"
    RAW_EMG2 = "d5060205-a904-deb9-4748-2c7f4a124842"
    RAW_EMG3 = "d5060305-a904-deb9-4748-2c7f4a124842"
    RAW_EMG4 = "d5060405-a904-deb9-4748-2c7f4a124842"


class MyoService(enum.Enum):
    """
    各个Service的UUID，参考低功耗蓝牙相关资料
    """
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
    """
    各个姿态，参考Myo官方指定的手势
    """
    POSE_REST = 0   # 放松
    POSE_FIST = 1   # 握拳
    POSE_WAVE_IN = 2    # 手腕向里
    POSE_WAVE_OUT = 3   # 手腕向外
    POSE_FINGERS_SPREAD = 4 # 手指伸开
    POSE_DOUBLE_TAP = 5 # 大拇指与中指相互敲击两下


class MyoMKU(enum.Enum):
    """
    手环外观颜色
    """
    BLACK_MYO = 1   # 黑色
    WHITE_MYO = 2   # 白色


class MyoEmgMode(enum.Enum):
    """
    Emg数据发送模式
    """
    NONE = 0
    SEND_EMG = 1    # 发送内部滤波之后的EMG数据
    SEND_EMG_RAW = 2    # 发送未滤波的EMG数据（原始数据）


class MyoImuMode(enum.Enum):
    """
    IMU数据发送模式
    """
    NONE = 0
    SEND_DATA = 1   # 发送数据
    SEND_EVENT = 2  # 发送事件
    SEND_ALL = 3    # 都发送
    SEND_RAW = 4    # 发送原始数据


class MyoClassifierMode(enum.Enum):
    """
    手环内部的分类器状态
    """
    DISABLED = 0    # 关闭
    ENABLED = 1     # 开启


class MyoClassifierEventType(enum.Enum):
    """
    手环内部的分类器事件类型
    """
    ARM_SYNCED = 1  # 手环同步事件
    ARM_UNSYNCED = 2    # 手环未同步事件
    POSE = 3    # 姿态事件
    UNLOCKED = 4    # 解锁事件
    LOCKED = 5  # 锁定事件
    SYNC_FAILED = 6 # 同步失败事件


class Arm(enum.Enum):
    """
    手臂类型
    """
    UNKNOWN = 0 # 未知
    RIGHT = 1   # 右手臂
    LEFT = 2    # 左手臂


class XDirection(enum.Enum):
    """
    手环佩戴方向
    """
    UNKNOWN = 0
    X_TOWARD_WRIST = 1  # 朝向手腕
    X_TOWARD_ELBOW = 2  # 朝向手肘


class Pose(enum.Enum):
    REST = 0
    FIST = 1
    WAVE_IN = 2
    WAVE_OUT = 3
    FINGERS_SPREAD = 4
    THUMB_TO_PINKY = 5
    UNKNOWN = 255