# coding=utf8
"""
Myo相关定义类
"""
import enum
import re
import time

from serial.tools.list_ports import comports

from Bean.bt import BT
from Bean.myo_packet import *
from Bean.myo_utils import *


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


class MyoStatus(enum.Enum):
    PENDING = 0
    SCANNING = 1
    CONNECTING = 2
    CONNECTED = 3
    DISCONNECTED = 4


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

    def __init__(self, tty=None, config=None, mac_address=""):
        """
        :param tty: 串口实例
        :param config: Myo配置文件，应传入myo_config实例
        :param both: if connect two myos
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
        self.mac_address = mac_address
        self.status = None

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

    def write_attr(self, conn, attr, val):
        if conn is not None:
            self.bt.write_attr(conn, attr, val)

    def read_attr(self, conn, attr):
        if conn is None:
            return None
        return self.bt.read_attr(conn, attr)

    def connect(self, timeout=None):
        """
        连接two myos
        :return:
        """
        # 停止之前的扫描和连接
        self.bt.end_scan()
        self.bt.disconnect(0)
        self.bt.disconnect(1)
        self.bt.disconnect(2)

        time_now = time.time()

        # 开始扫描
        print('scanning...')
        self.bt.discover()

        address = None

        while True:
            if timeout is not None and time.time() - time_now > timeout:
                break
            p = self.bt.recv_packet()
            print('scan response:', p)

            # Find Two Myo armband
            if p.payload.endswith(b'\x06\x42\x48\x12\x4A\x7F\x2C\x48\x47\xB9\xDE\x04\xA9\x01\x00\x06\xD5'):
                address = list(multiord(p.payload[2:8]))
                if self.mac_address == "":
                    break
                else:
                    if self.get_mac_address(address) == self.mac_address:
                        break
                # mac_address_judge = ":".join(map(lambda x: "%x" % x, reversed(list(multiord(p.payload[2:8])))))
                # if mac_address_judge == "cc:25:15:ee:2e:12":
        self.bt.end_scan()
        if address is None:
            # time out
            return MyoStatus.PENDING

        # make address:conn dict
        # use bt manager to connect
        conn_pkt = self.bt.connect(address)
        self.conn = multiord(conn_pkt.payload)[-1]
        self.bt.wait_event(3, 0)

        print('device name: %s' % self.get_name(self.conn))
        # 禁止休眠
        self.never_sleep(self.conn)
        self.set_lock(self.conn, MyoUnlockMode.HOLD)
        self.vibrate(self.conn, MyoVibrationMode.LONG)
        self.config_myo(self.config)

        def data_handler(p):
            # check whether is the command response packet
            if (p.cls, p.cmd) != (4, 5): return

            # attr is the handle value
            c, attr, typ = unpack('BHB', p.payload[:4])
            # print(attr)
            pay = p.payload[5:]

            if attr in (0x2B, 0x2E, 0x31, 0x34):
                # raw data 0 1
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
            elif attr == 0x23:
                # arm data
                typ, val, xdir, _, _, _ = unpack('6B', pay)

                if typ == 1:  # on arm
                    self.on_arm(Arm(val), XDirection(xdir))
                elif typ == 2:  # removed from arm
                    self.on_arm(Arm.UNKNOWN, XDirection.UNKNOWN)
                elif typ == 3:  # pose
                    self.on_pose(Pose(val))
            else:
                print('data with unknown attr: %02X %s' % (attr, p))

        self.bt.add_handler(data_handler)

        return MyoStatus.CONNECTED

    def disconnect(self):
        if self.conn is not None:
            # normal sleep
            self.normal_sleep(self.conn)
            self.bt.disconnect(self.conn)

    def config_myo(self, myo_config):
        """
        如果沒有配置文件则默认开启emg数据通道
        :param myo_config:
        :return:
        """
        if myo_config is None:
            return

        if myo_config.emg_enable:
            self.is_broadcast_data(self.conn, MyoHandler.EMG_CCC_HANDLE.value, True)
        elif myo_config.emg_raw_enable:
            self.is_broadcast_data(self.conn, MyoHandler.EMG_RAW_DATA_1_CCC_HANDLE.value, True)
            self.is_broadcast_data(self.conn, MyoHandler.EMG_RAW_DATA_2_CCC_HANDLE.value, True)
            self.is_broadcast_data(self.conn, MyoHandler.EMG_RAW_DATA_3_CCC_HANDLE.value, True)
            self.is_broadcast_data(self.conn, MyoHandler.EMG_RAW_DATA_4_CCC_HANDLE.value, True)

        if myo_config.imu_enable:
            self.is_broadcast_data(self.conn, MyoHandler.IMU_CCC_HANDLE.value, True)

        if myo_config.arm_enable:
            # 使能arm数据通知
            self.is_broadcast_data(self.conn, MyoHandler.ARM_CCC_HANDLE.value, True)

        self.is_enable_data(self.conn,
                            emg_enable=myo_config.emg_enable,
                            imu_enable=myo_config.imu_enable,
                            arm_enable=myo_config.arm_enable,
                            emg_raw_enable=myo_config.emg_raw_enable)

    def vibrate(self, conn, length):
        if length in range(1, 4):
            command = MyoVibrateCommandPacket(
                header=MyoCommandHeader(
                    command=MyoCommand.VIBRATE.value,
                    payload_size=1
                ),
                vibrate_type=length
            )
            self.write_attr(conn,
                            MyoHandler.COMMAND_INPUT_HANDLE.value,
                            command.get_bytes()
                            )

    def normal_sleep(self, conn):
        command = MyoSetSleepCommandPacket(
            header=MyoCommandHeader(
                command=MyoCommand.SET_SLEEP_MODE.value,
                payload_size=1
            ),
            sleep_mode=MyoSleepMode.NORMAL.value
        )
        self.write_attr(conn,
                        MyoHandler.COMMAND_INPUT_HANDLE.value,
                        command.get_bytes())

    def never_sleep(self, conn):
        command = MyoSetSleepCommandPacket(
            header=MyoCommandHeader(
                command=MyoCommand.SET_SLEEP_MODE.value,
                payload_size=1
            ),
            sleep_mode=MyoSleepMode.NEVER_SLEEP.value
        )
        self.write_attr(conn,
                        MyoHandler.COMMAND_INPUT_HANDLE.value,
                        command.get_bytes()
                        )

    def set_lock(self, conn, lock_type: MyoUnlockMode):
        """
        configure lock status
        :param conn: connection
        :param lock_type: lock type in MyoUnlockMode
        :return:
        """
        if lock_type in MyoUnlockMode:
            command = MyoUnlockCommandPacket(
                header=MyoCommandHeader(
                    command=MyoCommand.UNLOCK.value,
                    payload_size=1
                ),
                unlock_type=lock_type.value
            )
            self.write_attr(conn,
                            MyoHandler.COMMAND_INPUT_HANDLE.value,
                            command.get_bytes()
                            )

    def get_battery_level(self, conn):
        level = self.read_attr(conn, MyoHandler.BATTERY_LEVEL_HANDLE.value)
        # TODO: 验证Packet的内容
        return

    def get_firmware_version(self, conn):
        fw = self.read_attr(conn, 0x17)
        _, _, _, _, v0, v1, v2, v3 = unpack('BHBBHHHH', fw.payload)
        return v0, v1, v2, v3

    def get_name(self, conn):
        return self.read_attr(conn, 0x03).payload

    def is_broadcast_data(self, conn, handle, enable):
        """
        使能或关闭数据广播
        :param handle: 数据对应的CCC的handle
        :param enable: True or False
        :return:
        """
        if enable:
            # arm data need to write b'\x02\x00' to open, not b'\x01\x00'\
            # 写入命令让Myo广播对应的数据
            if handle == MyoHandler.ARM_CCC_HANDLE.value:
                self.write_attr(conn, handle, b'\x02\x00')
            else:
                self.write_attr(conn, handle, b'\x01\x00')
        else:
            self.write_attr(conn, handle, b'\x00\x00')

    def is_enable_data(self, conn,
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
            enable_code += b'\x02'
        else:
            enable_code += b'\x00'

        if imu_enable:
            enable_code += b'\x01'
        else:
            enable_code += b'\x00'

        self.write_attr(conn, 0x19, enable_code + b"\x00")

        if arm_enable:
            enable_code += b'\x01'
        else:
            enable_code += b'\x00'

        self.write_attr(conn, 0x19, enable_code)

    def add_emg_handler(self, h):
        self.emg_handlers.append(h)

    def add_imu_handler(self, h):
        self.imu_handlers.append(h)

    def add_pose_handler(self, h):
        self.pose_handlers.append(h)

    def add_arm_handler(self, h):
        self.arm_handlers.append(h)

    def remove_arm_handler(self, h):
        self.arm_handlers.remove(h)

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
        # 对数据进行矫正
        data = self.process_emg_raw_data(data)
        for h in self.emg_raw_handlers:
            h(data)

    def process_emg_raw_data(self, data):
        return tuple([x if x <= 128 else x - 256 for x in data])

    def get_mac_address(self, addr):
        """
        get myo mac address from packet
        :param addr: packet
        :return:
        """
        mac_address = ":".join(map(lambda x: "%x" % x, reversed(addr)))
        return mac_address

    # TODO: need to test
    def get_dongle_supported_connections_num(self):
        p = self.bt.get_connections_num()
        return unpack("B", p.payload)