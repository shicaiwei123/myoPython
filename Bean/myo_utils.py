"""
封装myo的一些常用函数
"""
import struct
import sys


def multichr(ords):
    """
    返回多个字符的bytes值
    :param ords:
    :return:
    """
    if sys.version_info[0] >= 3:
        return bytes(ords)
    else:
        return ''.join(map(chr, ords))


def multiord(b):
    if sys.version_info[0] >= 3:
        return list(b)
    else:
        return map(ord, b)


def pack(fmt, *args):
    return struct.pack('<' + fmt, *args)


def unpack(fmt, *args):
    return struct.unpack('<' + fmt, *args)


def text(scr, font, txt, pos, clr=(255, 255, 255)):
    scr.blit(font.render(txt, True, clr), pos)
