import logging
import signal

from bluepy.btle import Scanner, DefaultDelegate

from Bean.myo import MyoRaw
from Bean.myo_config import MyoConfig


class MyoHub:

    def __init__(self, myo_count=2):

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        signal.signal(signal.SIGINT, self.disconnect)

        self.myo_count = myo_count

        self.init_myos(
            self.scan_myos(myo_count=myo_count, scan_time=5.0, iface=1)
        )
        self.myo_list = list()

        self.handler = handler
        self.running = False

    def init_myos(self, myo_list):
        config = MyoConfig()
        config.classifier_enable = True
        config.imu_enable = True
        config.emg_enable = True

        for idx, dev in enumerate(myo_list):
            myo = MyoRaw(dev.addr, config=config)
            self.myo_list.append(myo)

    def connect_myos(self):
        for idx, myo in enumerate(self.myo_list):
            print("Waiting for connecting %s/%s myo", idx + 1, len(self.myo_list))
            myo.connect()


    def scan_myos(self, myo_count=2, scan_time=10.0, iface=0):
        """
        scan myo in scan_time seconds
        :param myo_count:
        :param scan_time:
        :param iface: index of hci
        :return: list of myos(ScanEntity Class)
        """
        myo_lists = []

        if not isinstance(myo_count, int):
            self.logger.warning("myo_count parameter is not Integer, use myo_count=2")
            myo_count = 2
        if not isinstance(scan_time, float):
            self.logger.warning("scan_time parameter is not Float, use scan_time=10.0")
            scan_time = 10.0
        if not isinstance(iface, int):
            self.logger.warning("iface parameter is not Integer, use iface=0")
            iface = 0
        scanner = Scanner(iface=iface).withDelegate(MyoScanDelegate())
        devices = scanner.scan(scan_time)
        for dev in devices:
            if dev.getValueText(6) == "4248124a7f2c4847b9de04a9010006d5":
                # find myo
                myo_lists.append(dev)
                self.logger.info("Discovered myo: %s, name: %s" % (dev.addr, dev.getValueText(9)))
                continue
        if len(myo_lists) != myo_count:
            self.logger.warning(
                "Cannot found enough myos, find count: %s, need count: %s" % (len(myo_lists), myo_count))
        return myo_lists


class MyoScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", scanEntry.addr)
        elif isNewData:
            print("Received new data from %s" % scanEntry.addr)


class Myo