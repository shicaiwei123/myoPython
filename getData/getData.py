# -*- coding: utf-8 -*-

import time
import logging
import sys
sys.path.append("..")
from Bean.myo_hub import MyoHub
from DataAnalysis.myoAnalysis import *
import redis
import json
import numpy as np
r = redis.Redis(host="127.0.0.1")

HAVE_PYGAME = False

global timeBegin

logging.basicConfig(level=logging.WARNING)


def init():
    """
    初始化一个myo实体
    :return: myo对象
    """
    global timeBegin
    m = MyoHub(myo_num=2)
    timeBegin = time.time()
    m.start()
    while not m.is_ready():
        continue
    return m


def _getOnceData(m):
    """
    获取一次手环刷新的数据。刷新率50hz
    :param m: Myo对象
    :return: 一次手势运动过程的数据，左右手的emg和imu数据以及右手的四元素数据
    """

    is_connecting = True
    while True:
        "阻塞于此获取数据"
        emgLeftData, emgRightData, imuLeftData, imuRightData = m.get_data()
        "如果手环和蓝牙断开连接了就会返回None，此时就要不断循环，等待手环连接并且正确返回数据"
        if emgLeftData is None and emgRightData is None and imuLeftData is None and imuRightData is None:
            logging.warning("reconnecting myo")
            is_connecting = False
            continue
        elif not is_connecting:
            is_connecting = True
            r.publish("log", json.dumps({"type": "mainLog", "data": "已重新连接手环"}))
            break
    "数据处理，除以20和100只是为了将数据缩小，没有特别含义"
    # print(emgLeftData, emgRightData, imuLeftData, imuRightData)
    emgRightData = list(emgRightData)
    qurt = list(imuRightData[0])
    qurt = np.array(qurt) / 100
    imuLeftData = list(imuLeftData[1] + imuLeftData[2])
    imuRightData = list(imuRightData[1] + imuRightData[2])

    # print(emgLeftData, emgRightData, imuLeftData, imuRightData)
    emgLeftCache = list(np.array(emgLeftData) / 100)
    emgRightCache = list(np.array(emgRightData) / 100)
    imuLeftCache = list(np.array(imuLeftData) / 20)
    imuRightCache = list(np.array(imuRightData) / 20)
    # print(emgLeftData, '\t', imuLeftCache[0:3], '\t', emgRightData, '\t', imuRightCache[0:3])

    return emgLeftCache, imuLeftCache, emgRightCache, imuRightCache, qurt



def _engery(emgData):
    """
    求emg数据的能量
    :param emgData: emg数据流
    :return:
    """
    emgArray = np.array(emgData)
    emgArray = emgArray
    emgSquare = np.square(emgArray)
    emgSum = np.sum(emgSquare)
    emgMean = emgSum / 5  # 在过去的0.1s内
    return emgMean


def gyoEngery(gyoData):
    """
    求gyo数据的能量
    :param gyoData: gyo数据流
    :return:
    """
    gyoData = np.array(gyoData)
    gyoData = gyoData * 10
    gyoData = gyoData / 100
    gyoSquare = np.square(gyoData)
    gyoSum = np.sum(gyoSquare)
    return gyoSum


threshold = 500
# 在原始数据基础上获取一次手势的数据
# 实现分段
# 如果把第一次的阈值也变小呢？


def getGestureData(m):
    """
    获取一次手势运动过程的数据。
    输入流数据，利用长度为5的滑动窗口计算能量。当能量大于一定值时开始存储数据，当能量连续低于一定数值时清空数据
    当能量大于一定阈值时，认为开始运动。并不是在认为开始运动之后才记录数据，而是单独的有一个记录和清空数据的阈值
    检测到两次运动后（伸手和收手），就认为完成一个手势运动的过程，返回数据
    :param m: myo对象
    :return: 右手手势运动的emg，imu数据；右手所有时刻下的emg，imu数据；
    左手手势运动的emg，imu数据；左手所有时刻下的emg，imu数据；右手所有时刻下的能量值，右手手势运动时的能量值
    """

    global threshold  # 能量阈值，当能量高于阈值是active状态，低于阈值是quiet状态

    beginSave = 10  # 当能量大于这个值，开始记录数据，防止记录平衡时的无效数据
    isSave = False  # 是否记录数据的标志位
    gyo = []
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
    "静止状态下的加速度和四元素数值，如果换了一个新的静止状态的姿势，这个数据需要重新测量"
    accQuiet = np.array([31, 28, 80])
    qurtQuiet = np.array([20, -24, -10])

    while True:
        "流数据获取"
        emgLeftCache, imuLeftCache, emgRightCache, imuRightCache, qurt = _getOnceData(m)
        gyo = gyo + imuRightCache[3:6]
        acc = np.array(imuRightCache[0:3])
        "流数据缓存"
        emgRightDataAll.append(emgRightCache)
        imuRightDataAll.append(imuRightCache)
        emgLeftDataAll.append(emgLeftCache)
        imuLeftDataAll.append(imuLeftCache)
        "流数据存储"
        if isSave:
            emgRightData.append(emgRightCache)
            imuRightData.append(imuRightCache)
            emgLeftData.append(emgLeftCache)
            imuLeftData.append(imuLeftCache)
        "运动检测和数据分割"
        if dataTimes < 5:
            dataTimes = dataTimes + 1
            '统计到5次数据后，也就是0.1s后'
        else:
            """"计算和静止状态下的四元素和加速度的差值
                和既定阈值相比，如果低于认为是回复了，不然继续循环"""
            accDiff = (acc[0] - accQuiet[0])**2 + (acc[1] - accQuiet[1])**2 + (acc[2] - accQuiet[2])**2
            qurtDiff = ((qurt[1] - qurtQuiet[0])**2 + (qurt[2] - qurtQuiet[1])**2 + (qurt[3] - qurtQuiet[2])**2)
            diffThreshold = qurtDiff + 0.05 * accDiff

            "计算陀螺仪能量"
            gyoE = gyoEngery(gyo)
            engeryData.append([gyoE])  # 存储所有的能量
            # nprint('\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t', gyoE)
            # print(accDiff)
            # print(diffThreshold)
            gyo = []
            dataTimes = 1
            "是否开始存储数据的阈值判断"
            if gyoE > beginSave:  # 开始存储数据
                isSave = True
                clearCounter = 1
            if isSave:             # 存储运动手势能量
                engerySeg.append([gyoE])

            "是否清空缓存的阈值判断"
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
            "是否开始运动的阈值判断"
            if gyoE > threshold:  # 如果大于阈值就算是活动状态，并且将安静状态清零
                gyoRightActive = gyoRightActive + 1
                gyoRightQuiet = 0
                clearCounter = 1

            else:
                gyoRightQuiet = gyoRightQuiet + 1
            "运动的次数是否已经满足阈值要求"
            if gyoRightQuiet > GyoRightQuietTimes - 1:
                "检测到运动的次数是否满足一定时长，不满足就认为是误触发，不采用"
                if gyoRightActive < 2:  # 滤波

                    gyoRightQuiet = 0

                    "静止时候的右手的加速度和四元素值的差的能量和阈值做对比，小于的情况下才能认为是静止了" \
                    "这一点和之前的运动检测是冲突丶，其实理论上这一点就够了，但是这一点其实是用来辅助的，后期也许还会优化"
                elif diffThreshold > 6000:
                    gyoRightQuiet = gyoRightQuiet  # 不做任何事,做最后的补充矫正，判断是不是静止
                    "完成一次检测"
                else:

                    gyoRightQuiet = 0

                    activeTimes = activeTimes + 1
                    threshold = 100
                    GyoRightQuietTimes = 2
                    "完成两次运动检测，完成数据收集，重置参数"
                    if activeTimes == ActiveTimes:
                        isSave = False
                        if len(emgRightData) != len(imuRightData):  # 接收到的emg和imu数据长度不等
                            print('wrong Data')
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
