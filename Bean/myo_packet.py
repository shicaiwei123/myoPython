"""
Myo各种功能的Packet类
"""
from Bean.myo_info import *


class MyoCommandHeader:
    def __init__(self, command: MyoCommand, payload_size):
        self.command = command.value
        self.len = payload_size


class MyoVibrateCommandPacket:
    def __init__(self, header: MyoCommandHeader, vibrate_type: MyoVibrationMode):
        self.header = header
        self.vibrate_type = vibrate_type.value

    def get_bytes(self):
        return bytes.fromhex(("{:02X}" * (self.header.len + 2)).format(
            self.header.command,
            self.header.len,
            self.vibrate_type))


class MyoDataEnableCommandPacket:
    def __init__(self, header: MyoCommandHeader, emg_mode:MyoEmgMode, imu_mode:MyoImuMode, classifier_mode:MyoClassifierMode):
        self.header = header
        self.emg_mode = emg_mode.value
        self.imu_mode = imu_mode.value
        self.classifier_mode = classifier_mode.value

    def get_bytes(self):
        return bytes.fromhex(("{:02X}" * (self.header.len + 2)).format(
            self.header.command,
            self.header.len,
            self.emg_mode,
            self.imu_mode,
            self.classifier_mode
        ))


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

    def __init__(self, header: MyoCommandHeader, sleep_mode: MyoSleepMode):
        self.header = header
        self.sleep_mode = sleep_mode.value

    def get_bytes(self):
        return bytes.fromhex(
            ("{:02X}" * (self.header.len + 2)).format(
                self.header.command,
                self.header.len,
                self.sleep_mode
            )
        )


class MyoUnlockCommandPacket:
    def __init__(self, header: MyoCommandHeader, unlock_type: MyoUnlockMode):
        self.header = header
        self.type = unlock_type.value

    def get_bytes(self):
        return bytes.fromhex(
            ("{:02X}" * (self.header.len + 2)).format(
                self.header.command,
                self.header.len,
                self.type
            )
        )
