# -*- coding: utf-8 -*-

import sys
import time

import pygame
from pygame.locals import *

from Bean.myo import MyoRaw
from Bean.myo_config import MyoConfig
from Bean.myo_hub import MyoHub
from myoAnalysis import *

HAVE_PYGAME = True

global timeBegin
dataCache = list(range(1, 105))  # 缓存5个
# 存储一个手势的数据
dataCounter = 0
dataLeftFresh = False
dataRightFresh = False
isFull = False

# 初始化
left_emg_list = []
right_emg_list = []
left_imu_list = []
right_imu_list = []

# 尝试导入pygame包，如果导入成功则显示emg数据轨迹，如果没有pygame包则不显示
if HAVE_PYGAME:
    w, h = 10, 10
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
            scr.fill((c, c, c), (w - D, i * h / 8, D, (i + 1) * h / 8 - i * h / 8))

    pygame.display.flip()
    last_vals = vals


def left_proc_emg(emg, times=[]):
    global left_emg_list
    global dataLeftFresh
    dataLeftFresh = True
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
    global right_emg_list
    global dataRightFresh
    dataRightFresh =True
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
    # 初始化myo实体
    # m = MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None,
    #            config=config)
    m = MyoHub(myo_num=2)

    # 连接
    # m.add_emg_handler(lambda emg: print(emg))
    # m.add_imu_handler(lambda a, b, c: print(a, b, c))
    # m.add_arm_handler(lambda arm, xdir: print('arm', arm, 'xdir', xdir))
    # m.add_pose_handler(lambda p: print('pose', p))
    # m.add_emg_raw_handler(proc_emg_raw)
    timeBegin = time.time()
    m.start()
    while not m.is_ready():
        continue
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
    global dataLeftFresh
    emgLeftCache = []
    imuLeftCache = []
    emgRightCache = []
    imuRightCache = []
    while True:
        emgLeftData, emgRightData, imuLeftData, imuRightData= m.get_data()
        # print(imuLeftData, imuRightData)
        emgLeftData=list(emgLeftData)
        emgRightData=list(emgRightData)
        imuLeftData=list(imuLeftData[0]+imuLeftData[1])
        imuRightData=list(imuRightData[0]+imuRightData[1])

        # print(emgLeftData, emgRightData, imuLeftData, imuRightData)
        emgLeftCache = list(np.array(emgLeftData) / 100)
        emgRightCache = list(np.array(emgRightData) / 100)
        imuLeftCache = list(np.array(imuLeftData) / 20)
        imuRightCache = list(np.array(imuRightData) / 20)
        # print(imuLeftCache[0:3], '\t', imuRightCache[0:3])
        timeNow = time.time() - timeBegin
        # print(right_emg_list, right_imu_list, left_emg_list, left_imu_list)
        # print(emgLeftCache, imuLeftCache, emgRightCache, imuRightCache)
        # return emgLeftCache, imuLeftCache, emgRightCache, imuRightCache
        # TODO: 询问
        return emgLeftCache, imuLeftCache,emgRightCache, imuRightCache

# 求emg数据能力用来判断阈值


def engery(emgData):
    emgArray = np.array(emgData)
    emgArray = emgArray
    emgSquare = np.square(emgArray)
    emgSum = np.sum(emgSquare)
    emgMean = emgSum / 5  # 在过去的0.1s内
    return emgMean


def gyoEngery(gyoData):
    gyoData = np.array(gyoData)
    gyoData = gyoData * 10
    gyoData = gyoData / 100
    gyoSquare = np.square(gyoData)
    gyoSum = np.sum(gyoSquare)
    return gyoSum


threshold = 700
# 在原始数据基础上获取一次手势的数据
# 实现分段
#


def getGestureData(m):
    t1 = time.time()
    global threshold  # 能量阈值，当能量高于阈值是active状态，低于阈值是quiet状态
    # 阈值在变化，如果是离散分割，那么第一次阈值大，第二次阈值小，连续分割阈值一样。
    # 根据实际分割的方式要修改代码中修改阈值的代码
    # 初始高阈值的作用有两个一个是将一些抖动噪声去掉，虽然开始激活存储数据，但是若是第一次
    beginSave = 10  # 当能量大于这个值，开始记录数据，防止记录平衡时的无效数据
    isSave = False  # 是否记录数据
    gyo = []  # 缓存gyo数据方便求能量，缓存5次
    dataTimes = 1  # 记录gyo存储的次数
    gyoRightQuiet = 0  # 记录gyo能量低于阈值的次数
    gyoRightActive = 0  # 记录gyo能量高于阈值的次数
    activeTimes = 0  # 记录能量峰的次数
    ActiveTimes = 2  # 几次能量峰表示一次手势，2是记录到两次能量峰的时候就表明记录了一次手势数据，修改这个参数可以进行连续和离散的手势分割
    GyoRightQuietTimes = 1  # 几次低于阈值表示一次能量峰的结束
    # 右手
    emgRightData = []  # 缓存手势数据
    imuRightData = []
    emgRightDataAll = []  # 缓存全部数据
    imuRightDataAll = []
    # 左手
    emgLeftData = []  # 缓存手势数据
    imuLeftData = []
    emgLeftDataAll = []  # 缓存全部数据
    imuLeftDataAll = []
    clearThreshold = 10
    clearCounter = 1
    engeryData = []
    engerySeg = []
    gyoLeft=[]
    while True:
        if HAVE_PYGAME:
            for ev in pygame.event.get():
                if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
                    np.save('test/engeryData', np.array(engeryData))
                    np.save('test/engerySeg', np.array(engerySeg))
                    # m.disconnect()
                    return 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000

        emgLeftCache, imuLeftCache, emgRightCache, imuRightCache = getOnceData(m)
        # print(imuLeftCache[0:3], '\t', imuRightCache[0:3])
        gyo = gyo + imuRightCache[3:6]
        gyoLeft=gyoLeft+imuLeftCache[3:6]
        # 采集带有时间的原始做判断
        # e = imuRightCache[8:11]
        # gyo = gyo + list(np.array(e) / 20)
        emgRightDataAll.append(emgRightCache)
        imuRightDataAll.append(imuRightCache)
        emgLeftDataAll.append(emgLeftCache)
        imuLeftDataAll.append(imuLeftCache)
        # emgRawRightAll.append(emgRightRaw)
        if isSave:  # 之前位置也放错了
            emgRightData.append(emgRightCache)
            imuRightData.append(imuRightCache)
            emgLeftData.append(emgLeftCache)
            imuLeftData.append(imuLeftCache)
        # 分割
        if dataTimes < 5:
            dataTimes = dataTimes + 1

        else:
            t2 = time.time()
            gyoLeftE = gyoEngery(gyoLeft)
            gyoE=gyoEngery(gyo)
            # print(gyoE)
            # print(gyoLeftE)
            gyoLeft=[]
            gyo = []
            engeryData.append([gyoE])  # 存储所有的能量
            dataTimes = 1
            if gyoE > beginSave:  # 开始存储数据
                isSave = True
                clearCounter = 1
            if isSave:             # 存储手势能量
                engerySeg.append([gyoE])
            # 滤除噪声和误触发带来的数据存储，避免数据的存储错误
            # 这个要和数据分割割裂开来，依据就在于clearCounter的上限的设计
            # 要比手势分割结束的记录次数高，不然会误清除
            # 本身设计的clear的阈值还低了，这样双重保险避免误清除
            if gyoE < clearThreshold:
                clearCounter = clearCounter + 1
            if clearCounter > 3:
                engerySeg = []
                emgRightData = []
                imuRightData = []
                emgLeftData = []
                imuLeftData = []
                clearCounter = 1
                isSave = False

            if gyoE > threshold:  # 如果大于阈值就算是活动状态，并且将安静状态清零
                gyoRightActive = gyoRightActive + 1
                gyoRightQuiet = 0
                clearCounter = 1
            # 需不需要也为0
            else:
                gyoRightQuiet = gyoRightQuiet + 1
            # 判断是否满足一次手势要求
            if gyoRightQuiet > GyoRightQuietTimes - 1:

                if gyoRightActive < 2:  # 滤波

                    gyoRightQuiet = 0
                else:

                    gyoRightQuiet = 0

                    activeTimes = activeTimes + 1
                    threshold = 30
                    GyoRightQuietTimes = 2
                    if activeTimes == ActiveTimes:
                        isSave = False
                        print(len(emgRightData))
                        if len(emgRightData) != len(imuRightData):  # 接收到的鞥和imu数据长度不等
                            print('wrong Data')
                            # ping一下？？
                        else:
                            gyoRightActive = 0
                            # print(gyoE)
                            emgRight = emgRightData
                            imuRight = imuRightData
                            emgLeft = emgLeftData
                            imuLeft = imuLeftData
                            emgRightData = []
                            imuRightData = []
                            emgLeftData = []
                            imuLeftData = []
                            activeTimes = 0
                            threshold = 700
                            t3=time.time()
                            # print(t3-t2)


                            GyoRightQuietTimes = 1
                            return emgRight, imuRight, emgRightDataAll, imuRightDataAll,\
                                emgLeft, imuLeft, emgLeftDataAll, imuLeftDataAll, engeryData, engerySeg
                            # print('ok')
