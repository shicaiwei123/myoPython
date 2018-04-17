import logging
from binascii import hexlify

logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.DEBUG)


def test_myo_one(handle, value):
    print("one: %s", hexlify(value))


def test_myo_two(handle, value):
    print("two: %s", hexlify(value))


class Test:
    def __init__(self):
        self.list = []

    def t(self):
        self.list.append(1)


class T:
    def __init__(self, test):
        self.pool = test

    def test(self):
        self.pool.t()


if __name__ == '__main__':
    t = Test()
    t1 = T(t)
    t2 = T(t)
    t1.test()
    t2.test()
    print(len(t.list))