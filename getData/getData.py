# -*- coding: utf-8 -*-

import sys
import time

from Bean.myo_hub import MyoHub
from myoAnalysis import *

HAVE_PYGAME = False

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

last_vals = None

# 绘图函数，使用pygame绘制emg数据



# def __left_proc_emg(emg, times=[]):
#     global left_emg_list
#     global dataLeftFresh
#     dataLeftFresh = True
#     t = [1.1]
#     global emgCount
#     # if HAVE_PYGAME:
#     #     # update pygame display
#     #     plot(scr, [e / 2000. for e in emg])
#
#     # print frame rate of received data
#     times.append(time.time())
#     if len(times) > 20:
#         # print((len(times) - 1) / (times[-1] - times[0]))
#         times.pop(0)
#     if emg[0] > 0:
#         t1 = (time.time() - timeBegin)
#         # print(t1)
#         # print(emg)
#         emg = list(emg)
#         t[0] = t1
#         data = t + emg
#         left_emg_list = data
#
#
# def __right_proc_emg(emg, times=[]):
#     global right_emg_list
#     global dataRightFresh
#     dataRightFresh = True
#     t = [1.1]
#     global emgCount
#     # if HAVE_PYGAME:
#     #     # update pygame display
#     #     plot(scr, [e / 2000. for e in emg])
#
#     # print frame rate of received data
#     times.append(time.time())
#     if len(times) > 20:
#         # print((len(times) - 1) / (times[-1] - times[0]))
#         times.pop(0)
#
#     if emg[0] > 0:
#         t1 = (time.time() - timeBegin)
#         # print(t1)
#         # print(emg)
#         emg = list(emg)
#         t[0] = t1
#         data = t + emg
#         right_emg_list = data
#
#
# def __left_imu_proc(a, b, c):
#     global imuCount
#     global left_imu_list
#     # imuCount = imuCount + 1
#     t = [1.1]
#     a = list(a)
#     b = list(b)
#     c = list(c)
#     data = c
#     # if HAVE_PYGAME:
#     #     # update pygame display
#     #     plot(scr, [e / 2000. for e in data])
#     global timeBegin
#     t1 = (time.time() - timeBegin)
#     # print(t1)
#     # print(a, b, c)
#     t[0] = t1
#     c = t + a + b + c
#     left_imu_list = c
#
#
# def __right_imu_proc(a, b, c):
#     global imuCount
#     global right_imu_list
#     # imuCount = imuCount + 1
#     t = [1.1]
#     # t[0] = int(t1*10000)
#     a = list(a)
#     b = list(b)
#     c = list(c)
#     data = c
#     # if HAVE_PYGAME:
#     #     # update pygame display
#     #     plot(scr, [e / 2000. for e in data])
#     global timeBegin
#     t1 = (time.time() - timeBegin)
#     t[0] = t1
#     # print(t1)
#     # print(a, b, c)
#     c = t + a + b + c
#     right_imu_list = c


def init():
    # 初始化配置，并打开emg数据开关
    global timeBegin
    # 初始化myo实体
    m = MyoHub(myo_num=2)
    timeBegin = time.time()
    m.start()
    while not m.is_ready():
        continue
    return m

def _getOnceData(m):
    """
    Get One DataSet From Myo
    :param m: Myo
    :return: Emg DataSet and Imu DataSet( Only Accelerator Data and Gyro Data)
    """
    global dataCounter
    global dataLeftFresh
    while True:
        emgLeftData, emgRightData, imuLeftData, imuRightData = m.get_data()
        # print(emgLeftData, emgRightData, imuLeftData, imuRightData)
        # emgLeftData=list(emgLeftData)
        emgRightData = list(emgRightData)
        qurt=list(imuRightData[0])
        qurt=np.array(qurt)/100
        imuLeftData = list(imuLeftData[1] + imuLeftData[2])
        imuRightData = list(imuRightData[1] + imuRightData[2])

        # print(emgLeftData, emgRightData, imuLeftData, imuRightData)
        emgLeftCache = list(np.array(emgLeftData) / 100)
        emgRightCache = list(np.array(emgRightData) / 100)
        imuLeftCache = list(np.array(imuLeftData) / 20)
        imuRightCache = list(np.array(imuRightData) / 20)
        # print(emgLeftData, '\t', imuLeftCache[0:3], '\t', emgRightData, '\t', imuRightCache[0:3])
        timeNow = time.time() - timeBegin
        #print(emgLeftCache, imuLeftCache, emgRightCache, imuRightCache)
        # print(imuRightCache)
        #print(qurt)
        # TODO: 询问
        return emgLeftCache, imuLeftCache, emgRightCache, imuRightCache,qurt

# 求emg数据能力用来判断阈值


def _engery(emgData):
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


threshold = 500
# 在原始数据基础上获取一次手势的数据
# 实现分段
#如果把第一次的阈值也变小呢？


def getGestureData(m):
    """
    会缓存所有的数据，能量的手势的
    会实时的进行能量的判断，大于阈值为活动，小于阈值为静止
    会统计活动和静止的次数
    静止大于一定值就认为结束，清空。
    清空的阈值和结束的阈值可能是不一样的
    开始存储和开始的阈值也是不一样的
    """
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
    gyoLeft = []
    timeBegin = time.time()
    accQuiet=np.array([31,28,80])
    qurtQuiet=np.array([20,-24,-10])
    i = 1
    while True:
        emgLeftCache, imuLeftCache, emgRightCache, imuRightCache,qurt = _getOnceData(m)
        # print(imuLeftCache[3:6], '\t', imuRightCache[3:6])
        gyo = gyo + imuRightCache[3:6]
        acc=np.array(imuRightCache[0:3])
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
            """"计算和禁止状态下的四元素和加速度的差值
                和既定阈值相比，如果低于认为是回复了，不然继续循环"""
            accDiff=(acc[0]-accQuiet[0])**2+(acc[1]-accQuiet[1])**2+(acc[2]-accQuiet[2])**2
            qurtDiff=((qurt[1]-qurtQuiet[0])**2+(qurt[2]-qurtQuiet[1])**2+(qurt[3]-qurtQuiet[2])**2)
            diffThreshold=qurtDiff+0.05*accDiff
            gyoE = gyoEngery(gyo)
            # nprint('\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', gyoE)
            # print(accDiff)
            # print(diffThreshold)
            gyo = []
            engeryData.append([gyoE])  # 存储所有的能量
            dataTimes = 1
            if gyoE > beginSave:  # 开始存储数据
                if i == 1:
                    # tStart = time.time()
                    i = i + 1
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
               # elif diffThreshold>6000:
                #    gyoRightQuiet=gyoRightQuiet   #不做任何事,做最后的补充矫正，判断是不是静止
                else:

                    gyoRightQuiet = 0

                    activeTimes = activeTimes + 1
                    threshold = 100
                    GyoRightQuietTimes = 2
                    if activeTimes == ActiveTimes:
                        isSave = False
                        # t3 = time.time()
                        # print(t3 - tStart)
                        # print((len(emgRightData) / 5) * 0.1)  # 理论时间
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
                            threshold = 500

                            GyoRightQuietTimes = 1
                            return emgRight, imuRight, emgRightDataAll, imuRightDataAll,\
                                emgLeft, imuLeft, emgLeftDataAll, imuLeftDataAll, engeryData, engerySeg
                            # print('ok')
