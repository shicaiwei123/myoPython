# -*- coding: utf-8 -*-

import time

import pygame
from pygame.locals import *

from Bean.myo_handler import MyoDefaultHandler
from Bean.myo_monitor_process import MyoMonitorProcess
from myoAnalysis import *

HAVE_PYGAME = True

global timeBegin

dataCache = list(range(1, 105))  # 缓存5个
# 存储一个手势的数据
dataCounter = 0
dataFresh = False
isFull = False

# 初始化
left_emg_list = []
right_emg_list = []
left_imu_list = []
right_imu_list = []

# 尝试导入pygame包，如果导入成功则显示emg数据轨迹，如果没有pygame包则不显示
w, h = 1200, 500
scr = pygame.display.set_mode((w, h))
# scr1 = pygame.display.set_mode((w, h))
last_vals = None


# 绘图函数，使用pygame绘制emg数据
def plot(scr, vals):
    global w, h
    DRAW_LINES = True

    global last_vals
    if last_vals is None:
        last_vals = vals
        return
    D = 5
    scr.scroll(-D)
    scr.fill((0, 0, 0), (w - D, 0, w, h))
    for i, (u, v) in enumerate(zip(last_vals, vals)):
        if DRAW_LINES:
            pygame.draw.line(scr, (0, 255, 0),
                             (w - D, int(h / 8 * (i + 1 - u))),
                             (w, int(h / 8 * (i + 1 - v))))
            pygame.draw.line(scr, (255, 255, 255),
                             (w - D, int(h / 8 * (i + 1))),
                             (w, int(h / 8 * (i + 1))))
        else:
            c = int(255 * max(0, min(1, v)))
            scr.fill((c, c, c), (w - D, i * h / 8, D, (i + 1) * h / 8 - i * h / 8));

    pygame.display.flip()
    last_vals = vals


def left_proc_emg(emg, times=[]):
    global dataFresh
    global left_emg_list
    dataFresh = True
    t = [1.1]
    global emgCount
    # if HAVE_PYGAME:
    #     # update pygame display
    #     plot(scr, [e / 2000. for e in emg])

    # print(emg)

    # print frame rate of received data
    times.append(time.time())
    if len(times) > 20:
        # print((len(times) - 1) / (times[-1] - times[0]))
        times.pop(0)
    if emg[0] > 0:
        t1 = (time.time() - timeBegin)
        emg = list(emg)
        t[0] = t1
        data = t + emg
        left_emg_list = data


def emg_proc(emg, times=[]):
    global dataFresh
    global right_emg_list
    dataFresh = True
    t = [1.1]
    global emgCount
    if HAVE_PYGAME:
        # update pygame display
        plot(scr, [e / 2000. for e in emg])

    # print(emg)

    # print frame rate of received data
    times.append(time.time())
    if len(times) > 20:
        # print((len(times) - 1) / (times[-1] - times[0]))
        times.pop(0)

    if emg[0] > 0:
        t1 = (time.time() - timeBegin)
        emg = list(emg)
        t[0] = t1
        data = t + emg
        right_emg_list = data


def left_imu_proc(a, b, c):
    global imuCount
    global left_imu_list
    # imuCount = imuCount + 1
    t = [1.1]
    # print(a,b,c)
    global timeBegin
    t1 = (time.time() - timeBegin)
    # print(t1)
    t[0] = t1
    # t[0] = int(t1*10000)
    a = list(a)
    b = list(b)
    c = list(c)
    data = c
    # if HAVE_PYGAME:
    #     # update pygame display
    #     plot(scr, [e / 2000. for e in data])
    c = t + a + b + c
    left_imu_list = c


def imu_proc(a, b, c):
    global imuCount
    global right_imu_list
    # imuCount = imuCount + 1
    t = [1.1]
    # print(a,b,c)
    global timeBegin
    t1 = (time.time() - timeBegin)
    # print(t1)
    t[0] = t1
    # t[0] = int(t1*10000)
    a = list(a)
    b = list(b)
    c = list(c)
    data = c
    # if HAVE_PYGAME:
    #     # update pygame display
    #     plot(scr, [e / 2000. for e in data])
    c = t + a + b + c
    right_imu_list = c


def init():
    # 初始化配置，并打开emg数据开关
    global timeBegin
    m = MyoMonitorProcess(myo_count=2)

    class MyoDataHandler(MyoDefaultHandler):

        def __init__(self):
            super().__init__()

        def imu_handler(self, quat, acc, gyro):
            imu_proc(quat, acc, gyro)

        def emg_handler(self, emg):
            emg_proc(emg)

    m.myo_hub.add_data_handlers(MyoDataHandler())
    m.start()
    timeBegin = time.time()

    return m


#
def getOnceData(m):
    """
    Get One DataSet From Myo
    :param m: Myo
    :return: Emg DataSet and Imu DataSet( Only Accelerator Data and Gyro Data)
    """
    global left_emg_list
    global left_imu_list
    global dataCounter
    global dataFresh
    emgLeftCache = []
    imuLeftCache = []
    emgRightCache = []
    imuRightCache = []
    while True:

        if dataFresh:
            emgLeftCache = left_emg_list[1:9]
            imuLeftCache = left_imu_list[5:11]
            emgRightCache = right_emg_list[1:9]
            imuRightCache = right_imu_list[5:11]
            dataFresh = False
            emgLeftCache = list(np.array(emgLeftCache) / 100)
            emgRightCache = list(np.array(emgRightCache) / 100)
            imuLeftCache = list(np.array(imuLeftCache) / 20)
            imuRightCache = list(np.array(imuRightCache) / 20)
            return emgLeftCache, imuLeftCache, emgRightCache, imuRightCache


# 求emg数据能力用来判断阈值
def engery(emgData):
    emgArray = np.array(emgData)
    emgArray = emgArray
    emgSquare = np.square(emgArray)
    emgSum = np.sum(emgSquare)
    emgMean = emgSum / 5  # 在过去的0.1s内
    return emgMean


Threshold = 15


# 在原始数据基础上获取一次手势的数据
# 实现分段
#
def getGestureData(m):
    global Threshold
    active = 1
    quiet = 1
    dataTimes = 1
    emgLeftData = []
    imuLeftData = []
    emgRightData = []
    imuRightData = []
    emg = []  # 缓存5次
    while True:
        if HAVE_PYGAME:
            for ev in pygame.event.get():
                if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
                    return 10000, 10000
                    m.disconnect()
                    break

        emgLeftCache, imuLeftCache, emgRightCache, imuRightCache = getOnceData(m)
        # print(emgCache )
        # print(imuCache)
        emgLeftData.append(emgLeftCache)
        imuLeftData.append(imuLeftCache)
        emgRightData.append(emgRightCache)
        imuRightData.append(imuRightCache)
        emg = emg + emgRightCache
        # fenge
        if dataTimes < 5:
            dataTimes = dataTimes + 1

        else:
            E = engery(emg)
            l = len(emg)
            emg = []
            dataTimes = 1
            # print(E)
            if E > Threshold:
                active = active + 1
                quiet = 1
            else:
                quiet = quiet + 1
            if quiet > 3:
                if active > 5:
                    return emgLeftData, imuLeftData, emgRightData, imuRightData
                    print("新手势")
                else:  # 重置
                    dataTimes = 1
                    active = 1
                    quiet = 1
                    emgLeftData = []
                    imuLeftData = []
                    emgRightData = []
                    imuRightData = []
