"""
Myo各种功能的Packet类
"""
import enum


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
    SET_SLEEP_MODE = 5
    UNLOCK = 6
    USER_ACTION = 7


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


class MyoCommandHeader:
    def __init__(self, command, payload_size):
        self.command = command
        self.len = payload_size


class MyoWriteAttrCommandPacket:
    def __init__(self, header: MyoCommandHeader, attr_handle: int, len: int, payload):
        self.header = header
        self.attr_handle = attr_handle
        self.len = len
        self.payload = payload


class MyoReadAttrCommandPacket:
    def __init__(self, header: MyoCommandHeader, attr_handle: int):
        self.header = header
        self.attr_handle = attr_handle


class MyoVibrateCommandPacket:
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
    Power off
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
    Normal Sleep or UnSleep
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