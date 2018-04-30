# -*- coding: utf-8 -*-

import sys
import time

import pygame
from pygame.locals import *

from Bean.myo import MyoRaw
from Bean.myo_config import MyoConfig
from Bean.myo_hub import MyoHub
from myoAnalysis import *

HAVE_PYGAME = False

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
if HAVE_PYGAME:
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
    global left_emg_list

    t = [1.1]
    global emgCount
    # if HAVE_PYGAME:
    #     # update pygame display
    #     plot(scr, [e / 2000. for e in emg])


    # print frame rate of received data
    times.append(time.time())
    if len(times) > 20:
        # print((len(times) - 1) / (times[-1] - times[0]))
        times.pop(0)
    if emg[0] > 0:
        t1 = (time.time() - timeBegin)
        # print(t1)
        # print(emg)
        emg = list(emg)
        t[0] = t1
        data = t + emg
        left_emg_list = data


def right_proc_emg(emg, times=[]):
    global dataFresh
    dataFresh = True
    global right_emg_list
    t = [1.1]
    global emgCount
    if HAVE_PYGAME:
        # update pygame display
        plot(scr, [e / 2000. for e in emg])


    # print frame rate of received data
    times.append(time.time())
    if len(times) > 20:
        # print((len(times) - 1) / (times[-1] - times[0]))
        times.pop(0)

    if emg[0] > 0:
        t1 = (time.time() - timeBegin)
        # print(t1)
        # print(emg)
        emg = list(emg)
        t[0] = t1
        data = t + emg
        right_emg_list = data


def left_imu_proc(a, b, c):
    global imuCount
    global left_imu_list
    # imuCount = imuCount + 1
    t = [1.1]
    a = list(a)
    b = list(b)
    c = list(c)
    data = c
    # if HAVE_PYGAME:
    #     # update pygame display
    #     plot(scr, [e / 2000. for e in data])
    global timeBegin
    t1 = (time.time() - timeBegin)
    # print(t1)
    # print(a, b, c)
    t[0] = t1
    c = t + a + b + c
    left_imu_list = c



def right_imu_proc(a, b, c):
    global imuCount
    global right_imu_list
    # imuCount = imuCount + 1
    t = [1.1]
    # t[0] = int(t1*10000)
    a = list(a)
    b = list(b)
    c = list(c)
    data = c
    # if HAVE_PYGAME:
    #     # update pygame display
    #     plot(scr, [e / 2000. for e in data])
    global timeBegin
    t1 = (time.time() - timeBegin)
    t[0] = t1
    # print(t1)
    # print(a, b, c)
    c = t + a + b + c
    right_imu_list = c


def init():
    # 初始化配置，并打开emg数据开关
    global timeBegin
    config = MyoConfig()
    config.emg_enable = True
    config.imu_enable = True
    config.arm_enable = False
    config.emg_raw_enable = True

    # 初始化myo实体
    # m = MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None,
    #            config=config)
    m = MyoHub()

    # 连接
    m.add_left_myo_imu_handler(left_imu_proc)
    m.add_left_myo_emg_handler(left_proc_emg)

    # 添加各种数据的回调
    m.add_right_myo_imu_handler(right_imu_proc)
    m.add_right_myo_emg_handler(right_proc_emg)
    # m.add_emg_handler(lambda emg: print(emg))
    # m.add_imu_handler(lambda a, b, c: print(a, b, c))
    # m.add_arm_handler(lambda arm, xdir: print('arm', arm, 'xdir', xdir))
    # m.add_pose_handler(lambda p: print('pose', p))
    # m.add_emg_raw_handler(proc_emg_raw)
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
        m.run(1)
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
            timeNow=time.time()-timeBegin
            print(right_emg_list,right_imu_list,left_emg_list,left_imu_list)
            # print(emgLeftCache, imuLeftCache, emgRightCache, imuRightCache)
            return emgLeftCache,imuLeftCache, emgRightCache, imuRightCache


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

        emgLeftCache,imuLeftCache, emgRightCache, imuRightCache = getOnceData(m)
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
                quiet=1
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