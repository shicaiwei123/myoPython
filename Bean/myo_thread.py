import threading
import enum
import logging


class MyoStatus(enum.Enum):
    PENDING = 0
    SCANNING = 1
    CONNECTING = 2
    CONNECTED = 3


class MyoThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        # initial status
        self.status = MyoStatus.PENDING
        self.myo = None
        self.logger = logging.getLogger(__name__)
        self.kill_received = False
        self.is_disconnected = False

    def run(self):
        """
        connect to a myo and read data from it
        when myo is disconnected, change to scanning status
        :return:
        """
        self.status = MyoStatus.CONNECTING
        self.myo = connect_rand_myo(timeout=30)
        if self.myo is None:
            self.logger.error("Timeout!! Cannot connect to myo armbands")
            return

        self.status = MyoStatus.CONNECTED

        while not self.kill_received:
            try:
                self.myo.run(1)
            except Exception as e:
                pass



