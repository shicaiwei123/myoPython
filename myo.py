# coding=utf8
"""
Myo相关定义类
"""
import re
import enum

import time

from bt import BT
from serial.tools.list_ports import comports
from myo_utils import *


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


class MyoRaw(object):
    """Implements the Myo-specific communication protocol."""

    def __init__(self, tty=None, config=None):
        """
        :param tty: 串口实例
        :param config: Myo配置文件，应传入myo_config实例
        """
        if tty is None:
            tty = self.detect_tty()
        if tty is None:
            raise ValueError('Myo dongle not found!')

        self.bt = BT(tty)
        self.conn = None
        self.config = config
        self.emg_handlers = []
        self.imu_handlers = []
        self.arm_handlers = []
        self.pose_handlers = []
        self.emg_raw_handlers = []

    def detect_tty(self):
        """
        检测tty
        :return:
        """
        for p in comports():
            if re.search(r'PID=2458:0*1', p[2]):
                print('using device:', p[0])
                return p[0]
        return None

    def run(self, timeout=None):
        self.bt.recv_packet(timeout)

    def write_attr(self, attr, val):
        if self.conn is not None:
            self.bt.write_attr(self.conn, attr, val)

    def read_attr(self, attr):
        if self.conn is None:
            return None
        return self.bt.read_attr(self.conn, attr)

    def connect(self):
        """
        连接myo
        :return:
        """
        # 停止之前的扫描和连接
        self.bt.end_scan()
        self.bt.disconnect(0)
        self.bt.disconnect(1)
        self.bt.disconnect(2)

        # 开始扫描
        print('scanning...')
        self.bt.discover()

        while True:
            p = self.bt.recv_packet()
            print('scan response:', p)

            # Find Myo armband
            if p.payload.endswith(b'\x06\x42\x48\x12\x4A\x7F\x2C\x48\x47\xB9\xDE\x04\xA9\x01\x00\x06\xD5'):
                address = list(multiord(p.payload[2:8]))
                break
        self.bt.end_scan()

        # use bt manager to connect
        conn_pkt = self.bt.connect(address)
        self.conn = multiord(conn_pkt.payload)[-1]
        self.bt.wait_event(3, 0)

        v0, v1, v2, v3 = self.get_firmware_version()

        print('firmware version: %d.%d.%d.%d' % (v0, v1, v2, v3))

        is_old = (v0 == 0)

        if is_old:
            # old version
            ## don't know what these do; Myo Connect sends them, though we get data
            ## fine without them
            self.write_attr(0x19, b'\x01\x02\x00\x00')
            self.write_attr(0x2f, b'\x01\x00')
            self.write_attr(0x2c, b'\x01\x00')
            self.write_attr(0x32, b'\x01\x00')
            self.write_attr(0x35, b'\x01\x00')

            ## enable EMG data
            self.write_attr(0x28, b'\x01\x00')
            ## enable IMU data
            self.write_attr(0x1d, b'\x01\x00')

            ## Sampling rate of the underlying EMG sensor, capped to 1000. If it's
            ## less than 1000, emg_hz is correct. If it is greater, the actual
            ## framerate starts dropping inversely. Also, if this is much less than
            ## 1000, EMG data becomes slower to respond to changes. In conclusion,
            ## 1000 is probably a good value.
            C = 1000
            emg_hz = 50
            ## strength of low-pass filtering of EMG data
            emg_smooth = 100

            imu_hz = 50

            ## send sensor parameters, or we don't get any data
            self.write_attr(0x19, pack('BBBBHBBBBB', 2, 9, 2, 1, C, emg_smooth, C // emg_hz, imu_hz, 0, 0))
        else:
            print('device name: %s' % self.get_name())
            self.config_myo(self.config)

        ## add data handlers
        def data_handler(p):
            # check whether is the command response packet
            if (p.cls, p.cmd) != (4, 5): return

            # attr is the handle value
            c, attr, typ = unpack('BHB', p.payload[:4])
            pay = p.payload[5:]

            if attr in (0x2B, 0x2E, 0x31, 0x34):
                # raw data 0 1
                print(attr)
                emg_raw_data = unpack('16B', pay)
                self.on_emg_raw(emg_raw_data[:8])
                self.on_emg_raw(emg_raw_data[8:])

            elif attr == 0x27:
                # emg data
                vals = unpack('8HB', pay)
                emg = vals[:8]
                self.on_emg(emg)
            elif attr == 0x1c:
                # imu data
                vals = unpack('10h', pay)
                quat = vals[:4]
                acc = vals[4:7]
                gyro = vals[7:10]
                self.on_imu(quat, acc, gyro)
            # elif attr == 0x23:
            #     # arm data
            #     typ, val, xdir, _, _, _ = unpack('6B', pay)
            #
            #     if typ == 1:  # on arm
            #         self.on_arm(Arm(val), XDirection(xdir))
            #     elif typ == 2:  # removed from arm
            #         self.on_arm(Arm.UNKNOWN, XDirection.UNKNOWN)
            #     elif typ == 3:  # pose
            #         self.on_pose(Pose(val))
            else:
                print('data with unknown attr: %02X %s' % (attr, p))

        self.bt.add_handler(data_handler)
        # self.start_collection()

    def disconnect(self):
        if self.conn is not None:
            self.bt.disconnect(self.conn)

    def config_myo(self, myo_config):
        """
        如果沒有配置文件则默认开启emg数据通道
        :param myo_config:
        :return:
        """
        if myo_config is None:
            self.is_broadcast_data(MyoHandler.EMG_CCC_HANDLE.value, True)
            self.is_enable_data(emg_enable=True)
            return

        if myo_config.emg_enable:
            self.is_broadcast_data(MyoHandler.EMG_CCC_HANDLE.value, True)
        elif myo_config.emg_raw_enable:
            self.is_broadcast_data(MyoHandler.EMG_RAW_DATA_1_CCC_HANDLE.value, True)
            self.is_broadcast_data(MyoHandler.EMG_RAW_DATA_2_CCC_HANDLE.value, True)
            self.is_broadcast_data(MyoHandler.EMG_RAW_DATA_3_CCC_HANDLE.value, True)
            self.is_broadcast_data(MyoHandler.EMG_RAW_DATA_4_CCC_HANDLE.value, True)

        if myo_config.imu_enable:
            self.is_broadcast_data(MyoHandler.IMU_CCC_HANDLE.value, True)

        if myo_config.arm_enable:
            # 使能arm数据通知
            self.is_broadcast_data(MyoHandler.ARM_CCC_HANDLE.value, True)

        self.is_enable_data(emg_enable=myo_config.emg_enable,
                            imu_enable=myo_config.imu_enable,
                            arm_enable=myo_config.arm_enable,
                            emg_raw_enable=myo_config.emg_raw_enable)

    def start_collection(self):
        """Myo Connect sends this sequence (or a reordering) when starting data
        collection for v1.0 firmware; this enables raw data but disables arm and
        pose notifications.
        """

        self.write_attr(0x19, b'\x09\x01\x01\x00\x00')

    def end_collection(self):
        """Myo Connect sends this sequence (or a reordering) when ending data collection
        for v1.0 firmware; this reenables arm and pose notifications, but
        doesn't disable raw data.
        """

        self.write_attr(0x19, b'\x09\x01\x00\x00\x00')

    def vibrate(self, length):
        if length in range(1, 4):
            # first byte tells it to vibrate; purpose of second byte is unknown
            self.write_attr(0x19, pack('3B', 3, 1, length))

    def get_firmware_version(self):
        fw = self.read_attr(0x17)
        _, _, _, _, v0, v1, v2, v3 = unpack('BHBBHHHH', fw.payload)
        return v0, v1, v2, v3

    def get_name(self):
        return self.read_attr(0x03).payload

    def is_broadcast_data(self, handle, enable):
        """
        使能或关闭数据广播
        :param handle: 数据对应的CCC的handle
        :param enable: True or False
        :return:
        """
        if enable:
            # 写入命令让Myo广播对应的数据
            self.write_attr(handle, b'\x01\x00')
        else:
            self.write_attr(handle, b'\x00\x00')

    def is_enable_data(self,
                       emg_enable=False,
                       imu_enable=False,
                       arm_enable=False,
                       emg_raw_enable=False):
        """
        打开或关闭数据开关
        :param emg_enable: 使能emg数据
        :param imu_enable: 使能imu数据
        :param arm_enable: 使能arm数据
        :param emg_raw_enable: 使能raw数据
        :return:
        """
        enable_code = b'\x01\x03'

        if emg_enable:
            enable_code += b'\x01'
        elif emg_raw_enable:
            enable_code += b'\x03'
        else:
            enable_code += b'\x00'

        if imu_enable:
            enable_code += b'\x01'
        else:
            enable_code += b'\x00'

        if arm_enable:
            enable_code += b'\x01'
        else:
            enable_code += b'\x00'

        self.write_attr(0x19, enable_code)

    def add_emg_handler(self, h):
        self.emg_handlers.append(h)

    def add_imu_handler(self, h):
        self.imu_handlers.append(h)

    def add_pose_handler(self, h):
        self.pose_handlers.append(h)

    def add_arm_handler(self, h):
        self.arm_handlers.append(h)

    def add_emg_raw_handler(self, h):
        self.emg_raw_handlers.append(h)

    def on_emg(self, emg):
        for h in self.emg_handlers:
            h(emg)

    def on_imu(self, quat, acc, gyro):
        for h in self.imu_handlers:
            h(quat, acc, gyro)

    def on_pose(self, p):
        for h in self.pose_handlers:
            h(p)

    def on_arm(self, arm, xdir):
        for h in self.arm_handlers:
            h(arm, xdir)

    def on_emg_raw(self, data):
        # index: emg sensor index
        for h in self.emg_raw_handlers:
            h(data)
