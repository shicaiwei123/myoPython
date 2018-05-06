import enum
# from serial import serial
import threading
import time

import serial

from myo_utils import *
from packet import Packet


class BTMessageID(enum.Enum):
    READ_ATTRIBUTE_BY_HANDLE = 4
    WRITE_ATTRIBUTE = 5


class BTMessageType(enum.Enum):
    COMMAND_MESSAGE = 0


class BTMessageClass(enum.Enum):
    ATTRIBUTE_CLIENT = 4


class BTEventMessageID(enum.Enum):
    PROCEDURE_COMPLETED = 1
    ATTRIBUTE_VALUE = 5


class BT(object):
    """Implements the non-Myo-specific details of the Bluetooth protocol."""

    def __init__(self, tty):
        self.ser = serial.Serial(port=tty, baudrate=9600, dsrdtr=1)
        self.buf = []
        self.lock = threading.Lock()
        self.handlers = []

    ## internal data-handling methods
    def recv_packet(self, timeout=None):
        t0 = time.time()
        self.ser.timeout = None
        while timeout is None or time.time() < t0 + timeout:
            if timeout is not None: self.ser.timeout = t0 + timeout - time.time()
            c = self.ser.read()
            if not c: return None

            ret = self.proc_byte(ord(c))
            if ret:
                if ret.typ == 0x80:
                    self.handle_event(ret)
                return ret

    def recv_packets(self, timeout=.5):
        res = []
        t0 = time.time()
        while time.time() < t0 + timeout:
            p = self.recv_packet(t0 + timeout - time.time())
            if not p: return res
            res.append(p)
        return res

    def proc_byte(self, c):
        if not self.buf:
            if c in [0x00, 0x80, 0x08, 0x88]:
                self.buf.append(c)
            return None
        elif len(self.buf) == 1:
            self.buf.append(c)
            self.packet_len = 4 + (self.buf[0] & 0x07) + self.buf[1]
            return None
        else:
            self.buf.append(c)

        if self.packet_len and len(self.buf) == self.packet_len:
            p = Packet(self.buf)
            self.buf = []
            return p
        return None

    def handle_event(self, p):
        for h in self.handlers:
            h(p)

    def add_handler(self, h):
        self.handlers.append(h)

    def remove_handler(self, h):
        try:
            self.handlers.remove(h)
        except ValueError:
            pass

    def wait_event(self, cls, cmd):
        """
        等待命令的Event响应
        :param cls: 命令类别ID
        :param cmd: 命令ID
        :return:
        """
        res = [None]

        def h(p):
            if p.cls == cls and p.cmd == cmd:
                res[0] = p

        self.add_handler(h)
        while res[0] is None:
            self.recv_packet()

        self.remove_handler(h)
        return res[0]

    ## specific BLE commands
    def connect(self, addr):
        return self.send_command(6, 3, pack('6sBHHHH', multichr(addr), 0, 6, 6, 64, 0))

    def get_connections(self):
        return self.send_command(0, 6)

    def discover(self):
        return self.send_command(6, 2, b'\x01')

    def end_scan(self):
        return self.send_command(6, 4)

    def disconnect(self, h):
        return self.send_command(3, 0, pack('B', h))

    def read_attr(self, connection, attr_handle):
        self.send_command(
            BTMessageClass.ATTRIBUTE_CLIENT.value,
            BTMessageID.READ_ATTRIBUTE_BY_HANDLE.value,
            pack('BH', connection, attr_handle))
        return self.wait_event(BTMessageClass.ATTRIBUTE_CLIENT.value,
                               BTEventMessageID.ATTRIBUTE_VALUE.value)

    def read_attr_by_uuid(self, connection, attr_uuid):
        pass

    def write_attr(self, connection, msg_handle, val):
        # B->unsigned char
        # H->unsigned short
        self.send_command(
            BTMessageClass.ATTRIBUTE_CLIENT.value,
            BTMessageID.WRITE_ATTRIBUTE.value,
            pack('BHB', connection, msg_handle, len(val)) + val)
        return self.wait_event(BTMessageClass.ATTRIBUTE_CLIENT.value,
                               BTEventMessageID.PROCEDURE_COMPLETED.value
                               )

    def send_command(self, msg_class, msg_id, payload=b'', wait_resp=True):
        s = pack('4B',
                 BTMessageType.COMMAND_MESSAGE.value,
                 len(payload),
                 msg_class,
                 msg_id) + payload
        self.ser.write(s)

        while True:
            p = self.recv_packet()

            ## no timeout, so p won't be None
            if p.typ == 0: return p

            ## not a response: must be an event
            self.handle_event(p)
