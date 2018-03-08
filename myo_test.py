# -*- coding: utf-8 -*-
import xlwt

import sys
import numpy as np
from myoAnalysis import *


#isSave取True时时存储数据，取False时时分析数据
from myo import MyoRaw

import time

from myo_config import MyoConfig
import pygame
from pygame.locals import *
HAVE_PYGAME = True

global timeBegin

global arr1, arr2 ,arr1Temp ,arr2Temp   #缓存初始数据
dataCache=list(range(1,105))    #缓存5个
#存储一个手势的数据
dataCounter=0
dataFresh =False
isFull = False

#初始化
arr1=[]
arr1Temp=arr1
arr1.append(1)
arr2=[]
arr2.append(1)
arr2Temp=arr2


# 尝试导入pygame包，如果导入成功则显示emg数据轨迹，如果没有pygame包则不显示
w, h = 1200, 400
scr = pygame.display.set_mode((w, h))
last_vals = None
# 绘图函数，使用pygame绘制emg数据
def plot(scr, vals):
        global w,h
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

def proc_emg(emg, times=[]):
        global dataFresh
        global arr1
        dataFresh=True
        t=[1.1]
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
        if emg[0]>0:
            t1 = (time.time() - timeBegin)
            emg=list(emg)
            t[0]=t1
            data=t+emg
            arr1 = data


def imu_proc(a,b,c):
        global imuCount
        global arr2
        # imuCount = imuCount + 1
        t = [1.1]
        # print(a,b,c)
        global timeBegin
        t1=(time.time()-timeBegin)
        # print(t1)
        t[0] = t1
        # t[0] = int(t1*10000)
        a=list(a)
        b=list(b)
        c=list(c)
        c=t+a+b+c
        arr2 = c







def init():
    # 初始化配置，并打开emg数据开关
    global timeBegin
    config = MyoConfig()
    config.emg_enable = True
    config.imu_enable = True
    config.arm_enable = False
    config.emg_raw_enable = False

    # 初始化myo实体
    m = MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None,
               config=config)

    # 连接
    m.connect()

    # 添加各种数据的回调
    m.add_emg_handler(proc_emg)
    m.add_imu_handler(imu_proc)
    # m.add_emg_handler(lambda emg: print(emg))
    # m.add_imu_handler(lambda a, b, c: print(a, b, c))
    # m.add_arm_handler(lambda arm, xdir: print('arm', arm, 'xdir', xdir))
    # m.add_pose_handler(lambda p: print('pose', p))
    # m.add_emg_raw_handler(proc_emg)
    timeBegin = time.time()
    return  m

#获取0.1s内原始数据
def getData(m):
    global dataCounter
    global dataFresh
    emgCache=[]
    imuCache=[]
    while True:
        while True:
            m.run(1)
            if dataFresh:
                data = list(arr1) + list(arr2)
                # 缓存5个数据
                # emgCache[dataCounter * 8 + 0:dataCounter * 8 + 7] = arr1[1:8]
                # imuCache[dataCounter * 6 + 0:dataCounter * 6 + 5] = arr2[5:10]
                emgCache=emgCache+arr1[1:8]
                imuCache=imuCache+arr2[5:10]
                if dataCounter==5:
                    # dataCache[(dataCounter*21)+0:(dataCounter*21)+20]=data
                    # dataCounter=dataCounter+1
                    dataCounter=0
                    # isFull=True
                    break
                else:
                    dataCounter=dataCounter+1
                    print(data)
                dataFresh =False
        return emgCache ,imuCache
            # return data

#求emg数据能力用来判断阈值
def engery(emgData):
    emgArray = np.array(emgData)
    emgSquare = np.square(emgArray/100)
    emgSum = np.sum(emgSquare)
    emgMean=emgSum/5    #在过去的0.1s内
    return emgMean

Threshold=35
active=1
quiet=1
dataTimes=1
isFinish =False
#在原始数据基础上获取一次手势的数据
#实现分段
def getGestureDtat(m):
    global Threshold
    global active
    global quiet
    global dataTimes
    global isFinish
    emgData=[]
    imuData=[]
    while True:
         emgCache ,imuCache= getData(m)
         emgData=emgData+emgCache
         imuData=imuData+imuCache
         dataTimes=dataTimes+1
         E=engery(emgCache)
         print(E)
         if E>Threshold:
             active=active+1
         else:
             quiet=quiet+1
         if quiet>3:
             if active>5:
                return emgData,imuData
                print("新手势")
             else:          #重置
                dataTimes=1
                active=1
                quiet=1
                emgData=[]
                imuData=[]


isSave=True
if __name__ == '__main__':
    global isSave
    m = init()
    #如果是存储数据
    if isSave:
        emgData=[]
        imuData=[]
        threshold=[]
        try:
            while True:
                emg, imu = getData(m)
                emgData.append(emg)
                imuData.append(imu)
                E=engery(emg)
                threshold.append([E])
                if HAVE_PYGAME:
                   for ev in pygame.event.get():
                        if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):

                            testXlwt('emgData.xls', emgData)
                            testXlwt('imuData.xls', imuData)
                            testXlwt('threshold.xls', threshold)
                            raise KeyboardInterrupt()
                        elif ev.type == KEYDOWN:
                            if K_1 <= ev.key <= K_3:
                                m.vibrate(ev.key - K_0)
                            if K_KP1 <= ev.key <= K_KP3:
                                m.vibrate(ev.key - K_KP0)

        except KeyboardInterrupt:
            pass
        finally:
            m.disconnect()
    #否则是分析数据
    else:
         emg=[]
         imu=[]
         while True:
             emg,imu = getGestureDtat(m)
             #特征提取
             #识别


#测试阈值
#测试分割
#完成matlab
#联调