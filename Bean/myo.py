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
from Bean.myo_info import *

import logging


class MyoHandler(enum.Enum):
    """
    Myo 不同Handle的值和对应的意义
    CCC 代表相应数据的控制位，其值表示是否广播对应的数据以及广播的类型（通知/指示），详见低功耗蓝牙相关资料
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


class MyoRaw(object):
    """实现Myo特定的协议"""

    def __init__(self, tty=None, config=None, mac_address=""):
        """
        :param tty: 串口实例
        :param config: Myo配置文件，应传入myo_config实例
        :param mac_address: 待连接的Myo手环对应的mac地址，如果未指定，则表示任意一个手环
        """
        if tty is None:
            tty = self.detect_tty()
        if tty is None:
            raise ValueError('Myo dongle not found!')
        
        self.tty = tty
        self.bt = BT(tty)
        self.conn = None
        self.config = config
        self.emg_handlers = []
        self.imu_handlers = []
        self.arm_handlers = []
        self.pose_handlers = []
        self.emg_raw_handlers = []
        self.mac_address = mac_address
        self.logger = self.config_logger("MyoRaw")

    def config_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        return logger

    def detect_tty(self):
        """
        检测myo适配器是否存在
        :return:
        """
        for p in comports():
            if re.search(r'PID=2458:0*1', p[2]):
                print('using device:', p[0])
                return p[0]
        return None

    def run(self, timeout=None):
        """
        开始运行，接收手环发送的数据包
        :param timeout: 超时时间
        :return:
        """
        self.bt.recv_packet(timeout)

    def write_attr(self, conn, attr, val):
        if conn is not None:
            self.bt.write_attr(conn, attr, val)

    def read_attr(self, conn, attr):
        if conn is None:
            return None
        return self.bt.read_attr(conn, attr)

    def connect(self, timeout=30):
        """
        连接Myo手环
        :param timeout 连接超时时间
        :return:
        """
        # 停止之前的扫描和连接
        self.bt.end_scan()
        self.bt.disconnect(0)
        self.bt.disconnect(1)
        self.bt.disconnect(2)

        # 开始扫描
        self.logger.info("Start scanning using %s", self.tty)
        self.bt.discover()

        time_start = time.time()
        address = None

        while True:
            if time.time() - time_start > timeout:
                break

            p = self.bt.recv_packet()
            self.logger.info("Scan response: %s", p)

            # 识别到是Myo手环发出的广播报文
            if p.payload.endswith(b'\x06\x42\x48\x12\x4A\x7F\x2C\x48\x47\xB9\xDE\x04\xA9\x01\x00\x06\xD5'):
                # 从数据包中截取mac地址
                address = list(multiord(p.payload[2:8]))
                if self.mac_address == "":
                    break
                else:
                    # 如果手环的mac地址与指定的mac地址相同，则结束扫描
                    if self.get_mac_address(address) == self.mac_address.lower():
                        break
        self.bt.end_scan()
        
        if address is None:
            raise TimeoutError("Scan myo timeout using %s" % self.tty)

        # 连接手环
        conn_pkt = self.bt.connect(address)
        # 手环对应的连接地址
        self.conn = multiord(conn_pkt.payload)[-1]
        self.bt.wait_event(3, 0)
        self.logger.info("Device name: %s", self.get_name(self.conn))

        # 对手环进行配置
        self.config_myo(self.config)

        # 数据回调类，根据不同的数据类型调用不同的回调函数
        def data_handler(p):
            # check whether is the command response packet
            if (p.cls, p.cmd) != (4, 5): return

            # attr is the handle value
            c, attr, typ = unpack('BHB', p.payload[:4])
            # print(attr)
            pay = p.payload[5:]

            # emg原始数据类型
            if attr in (0x2B, 0x2E, 0x31, 0x34):
                # raw data 0 1
                emg_raw_data = unpack('16B', pay)
                self.on_emg_raw(emg_raw_data[:8])
                self.on_emg_raw(emg_raw_data[8:])

            # emg数据类型
            elif attr == 0x27:
                # emg data
                vals = unpack('8HB', pay)
                emg = vals[:8]
                self.on_emg(emg)
            # imu数据类型
            elif attr == 0x1c:
                vals = unpack('10h', pay)
                # 四元数
                quat = vals[:4]
                # 加速度数据
                acc = vals[4:7]
                # 陀螺仪数据
                gyro = vals[7:10]
                self.on_imu(quat, acc, gyro)
            elif attr == 0x23:
                # 手势数据类型
                typ, val, xdir, _, _, _ = unpack('6B', pay)

                if typ == 1:  # 手臂和佩戴方向
                    self.on_arm(Arm(val), XDirection(xdir))
                elif typ == 2:  # 未佩戴
                    self.on_arm(Arm.UNKNOWN, XDirection.UNKNOWN)
                elif typ == 3:  # 姿势数据
                    self.on_pose(Pose(val))
            else:
                print('data with unknown attr: %02X %s' % (attr, p))

        # 绑定数据回调类
        self.bt.add_handler(data_handler)

    def disconnect(self):
        """
        断开手环的连接
        :return:
        """
        if self.conn is not None:
            self.bt.disconnect(self.conn)

    def config_myo(self, myo_config):
        """
        根据myo_config配置Myo手环，打开或关闭相应的数据以及对应的数据通知
        :param myo_config: 配置类
        :return:
        """
        if myo_config is None:
            return
        # 是否使能emg数据通知
        if myo_config.emg_enable:
            self.is_broadcast_data(self.conn, MyoHandler.EMG_CCC_HANDLE.value, True)
        # 是否使能emg原始数据通知
        elif myo_config.emg_raw_enable:
            self.is_broadcast_data(self.conn, MyoHandler.EMG_RAW_DATA_1_CCC_HANDLE.value, True)
            self.is_broadcast_data(self.conn, MyoHandler.EMG_RAW_DATA_2_CCC_HANDLE.value, True)
            self.is_broadcast_data(self.conn, MyoHandler.EMG_RAW_DATA_3_CCC_HANDLE.value, True)
            self.is_broadcast_data(self.conn, MyoHandler.EMG_RAW_DATA_4_CCC_HANDLE.value, True)
        else:
            self.is_broadcast_data(self.conn, MyoHandler.EMG_CCC_HANDLE.value, False)

        # 是否使能imu数据通知
        if myo_config.imu_enable:
            self.is_broadcast_data(self.conn, MyoHandler.IMU_CCC_HANDLE.value, True)
        else:
            self.is_broadcast_data(self.conn, MyoHandler.IMU_CCC_HANDLE.value, False)

        # 是否使能arm数据通知
        if myo_config.arm_enable:
            self.is_broadcast_data(self.conn, MyoHandler.ARM_CCC_HANDLE.value, True)
        else:
            self.is_broadcast_data(self.conn, MyoHandler.ARM_CCC_HANDLE.value, False)

        # 根据配置项使能对应的数据监测
        self.is_enable_data(self.conn,
                            emg_enable=myo_config.emg_enable,
                            imu_enable=myo_config.imu_enable,
                            arm_enable=myo_config.arm_enable,
                            emg_raw_enable=myo_config.emg_raw_enable)

    def vibrate(self, length):
        """
        控制Myo手环震动
        :param length: 强度，范围1-4
        :return:
        """
        if length in range(1, 4):
            command = MyoVibrateCommandPacket(
                header=MyoCommandHeader(
                    command=MyoCommand.VIBRATE.value,
                    payload_size=1
                ),
                vibrate_type=length
            )
            self.write_attr(self.conn,
                            MyoHandler.COMMAND_INPUT_HANDLE.value,
                            command.get_bytes()
                            )

    def normal_sleep(self, conn):
        """
        控制Myo手环进入正常休眠模式
        :param conn: 连接，tty
        :return:
        """
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

    def never_sleep(self):
        """
        控制Myo手环永远不休眠
        :return:
        """
        command = MyoSetSleepCommandPacket(
            header=MyoCommandHeader(
                command=MyoCommand.SET_SLEEP_MODE.value,
                payload_size=1
            ),
            sleep_mode=MyoSleepMode.NEVER_SLEEP.value
        )
        self.write_attr(self.conn,
                        MyoHandler.COMMAND_INPUT_HANDLE.value,
                        command.get_bytes()
                        )

    def set_lock(self, conn, lock_type):
        """
        设置Myo手环锁定状态
        :param conn: 手环对应的连接地址
        :param lock_type: 锁定类型，参考MyoUnlockMode
        :return:
        """
        if lock_type in [x.value for x in MyoUnlockMode]:
            command = MyoUnlockCommandPacket(
                header=MyoCommandHeader(
                    command=MyoCommand.UNLOCK.value,
                    payload_size=1
                ),
                unlock_type=lock_type
            )
            self.write_attr(conn,
                            MyoHandler.COMMAND_INPUT_HANDLE.value,
                            command.get_bytes()
                            )

    def get_firmware_version(self, conn):
        """
        获得手环固件版本
        :param conn: 手环连接地址
        :return:
        """
        fw = self.read_attr(conn, 0x17)
        _, _, _, _, v0, v1, v2, v3 = unpack('BHBBHHHH', fw.payload)
        return v0, v1, v2, v3

    def get_name(self, conn):
        """
        获得手环的名称
        :param conn: 手环连接地址
        :return:
        """
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
        # 对数据进行矫正，由于采样的原始数据为0-256，而真实的数据为-128-128，所以需要做预处理
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
        print(mac_address)
        return mac_address
