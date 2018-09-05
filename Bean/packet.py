from .myo_utils import multichr, multiord


class Packet(object):
    """
    Myo数据包格式
    """
    def __init__(self, ords):
        self.typ = ords[0]
        self.cls = ords[2]
        self.cmd = ords[3]
        self.payload = multichr(ords[4:])

    def __repr__(self):
        return 'Packet(%02X, %02X, %02X, [%s])' % \
               (self.typ, self.cls, self.cmd,
                ' '.join('%02X' % b for b in multiord(self.payload)))
