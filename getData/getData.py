# -*- coding: utf-8 -*-
import xlwt

import sys
import time
import pygame
from pygame.locals import *
import numpy as np
from myoAnalysis import *
from Bean.myo import MyoRaw
from Bean.myo_config import MyoConfig

HAVE_PYGAME = True

global timeBegin

global arr1, arr2 ,arr1Temp ,arr2Temp   #缓存初始数据
dataCache=list(range(1,105))    #缓存5个
#存储一个手势的数据
dataCounter=0
emgDataFresh = False
isFull = False

#初始化
arr1=[]
arr2=[]
emg_raw_list = []


# 尝试导入pygame包，如果导入成功则显示emg数据轨迹，如果没有pygame包则不显示
w, h = 1200, 500
scr = pygame.display.set_mode((w, h))
# scr1 = pygame.display.set_mode((w, h))
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



def proc_emg_raw(emg_raw, times=[]):
    global emgDataFresh
    global emg_raw_list
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
    if emg_raw_list[0] > 0:
        t1 = (time.time() - timeBegin)
        emg_raw_list = list(emg_raw_list)
        t[0] = t1
        data = t + emg_raw
        emg_raw_list = data


def proc_emg(emg, times=[]):
        global scr2
        global emgDataFresh
        global arr1
        emgDataFresh=True
        t=[1.1]
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
        data=c
        if HAVE_PYGAME:
        #     # update pygame display
            plot(scr, [e / 2000. for e in data])
        c=t+a+b+c
        arr2 = c

def init():
    # 初始化配置，并打开emg数据开关
    global timeBegin
    config = MyoConfig()
    config.emg_enable = True
    config.imu_enable = True
    config.arm_enable = False
    config.emg_raw_enable = True

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
    m.add_emg_raw_handler(proc_emg_raw)
    timeBegin = time.time()
    return  m

#yicishuju
def getOnceData(m):
    global arr1
    global arr2
    global dataCounter
    global emgDataFresh
    global emg_raw_list
    while  True:
        m.run(1)
        if emgDataFresh:
            # print(arr1+arr2)
            emgCache=arr1[1:9]
            imuCache=arr2[5:11]
            emg_raw = emg_raw_list[1:9]
            emgDataFresh =False
            emgCache=list(np.array(emgCache)/100)
            emgRawCache = list(np.array(emg_raw)/100)
            imuCache=list(np.array(imuCache)/20)

            # if HAVE_PYGAME:
            #     # update pygame display
            #     plot(scr, [e / 2000. for e in data])
            return emgCache, imuCache, emgRawCache


#求emg数据能力用来判断阈值
def engery(emgData):
    emgArray = np.array(emgData)
    emgArray=emgArray
    emgSquare = np.square(emgArray)
    emgSum = np.sum(emgSquare)
    emgMean=emgSum/5    #在过去的0.1s内
    return emgMean

def gyoEngery(gyoData):
    gyoData=np.array(gyoData)
    gyoData=gyoData*10
    gyoData=gyoData/100
    gyoSquare=np.square(gyoData)
    gyoSum=np.sum(gyoSquare)
    return gyoSum

threshold=500
engeryData = []
engerySeg = []
#在原始数据基础上获取一次手势的数据
#实现分段
#
def getGestureData(m):
    global threshold   #能量阈值，当能量高于阈值是active状态，低于阈值是quiet状态
                       #阈值在变化，如果是离散分割，那么第一次阈值大，第二次阈值小，连续分割阈值一样。
                       #根据实际分割的方式要修改代码中修改阈值的代码
                       #初始高阈值的作用有两个一个是将一些抖动噪声去掉，虽然开始激活存储数据，但是若是第一次
    beginSave=5    #当能量大于这个值，开始记录数据，防止记录平衡时的无效数据
    isSave=False   #是否记录数据
    gyo=[]         #缓存gyo数据方便求能量，缓存5次
    dataTimes=1    #记录gyo存储的次数
    gyoRigthQuiet=0    #记录gyo能量低于阈值的次数
    gyoRigthActive=0   #记录gyo能量高于阈值的次数
    activeTimes=0      #记录能量峰的次数
    ActiveTimes=2      #几次能量峰表示一次手势，2是记录到两次能量峰的时候就表明记录了一次手势数据，修改这个参数可以进行连续和离散的手势分割
    GyoRigthQuietTimes=1 #几次低于阈值表示一次能量峰的结束
    emgRigthData=[]    #缓存手势数据
    imuRightData=[]
    emgRigthDataAll=[]    #缓存全部数据
    imuRightDataAll=[]
    global engeryData
    global engerySeg
    while True:
         if HAVE_PYGAME:
            for ev in pygame.event.get():
                if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
                    np.save('test/engeryData',np.array(engeryData))
                    np.save('test/engerySeg', np.array(engerySeg))
                    return 10000,10000,10000,10000,10000,10000
                    m.disconnect()
                    break
         emgRigthCache ,imuRigthCache,emgRigthRaw= getOnceData(m)
         gyo=gyo+imuRigthCache[4:6]
         emgRigthDataAll.append(emgRigthCache)
         imuRightDataAll.append(imuRigthCache)
         if isSave:                   #之前位置也放错了
             emgRigthData.append(emgRigthCache)
             imuRightData.append(imuRigthCache)
         #分割
         if dataTimes<5:
             dataTimes=dataTimes+1

         else:
             gyoE=gyoEngery(gyo)
             # print(gyoE)
             gyo=[]
             engeryData.append(gyoE)
             dataTimes=1
             if gyoE>beginSave:      #开始存储数据
                 isSave=True
             engeryData.append(gyoE) #存储所有的能量
             if isSave:             # 存储手势能量
                 engerySeg.append(gyoE)

             if gyoE>threshold:     #如果大于阈值就算是活动状态，并且将安静状态清零
                 gyoRigthActive=gyoRigthActive+1
                 gyoRigthQuiet=0
            #需不需要也为0
             else:
                 gyoRigthQuiet=gyoRigthQuiet+1
            #判断是否满足一次手势要求
             if gyoRigthQuiet>GyoRigthQuietTimes-1:

                 if gyoRigthActive<2:      #滤波

                     gyoRigthQuiet=0
                 else:

                     gyoRigthQuiet=0
                     gyoRigthActive=0
                     activeTimes=activeTimes+1
                     threshold=20
                     GyoRigthQuietTimes=2
                     if activeTimes==ActiveTimes:
                        isSave=False
                        print(len(emgRigthData))
                        if len(emgRigthData)!=len(imuRightData):   #接收到的鞥和imu数据长度不等
                            print('wrong Data')
                            #ping一下？？
                        else:
                            print(gyoE)
                            emgRight=emgRigthData
                            imuRight=imuRightData
                            emgRigthData=[]
                            imuRightData=[]
                            activeTimes=0
                            threshold=500
                            GyoRigthQuietTimes=1
                            return emgRight,imuRight,emgRigthDataAll,imuRightDataAll, engeryData, engerySeg
                            # print('ok')


#isSave取True时时存储数据，取False时时分析数据
# if __name__ == '__main__':
#
#
#     m = init()
#     #shifoubaocunshuju
#     isSave = False
#     #导入模型
#
#     #如果是存储数据
#     if isSave:
#         emgData=[]
#         imuData=[]
#         threshold=[]
#         try:
#             while True:
#                 emg, imu = getOnceData(m)
#                 emgData.append(emg)
#                 imuData.append(imu)
#                 E=engery(emg)
#                 threshold.append([E])
#                 if HAVE_PYGAME:
#                    for ev in pygame.event.get():
#                         if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
#                             testXlwt('emgData.xls', emgData)
#                             testXlwt('imuData.xls', imuData)
#                             testXlwt('threshold.xls', threshold)
#                             raise KeyboardInterrupt()
#                         elif ev.type == KEYDOWN:
#                             if K_1 <= ev.key <= K_3:
#                                 m.vibrate(ev.key - K_0)
#                             if K_KP1 <= ev.key <= K_KP3:
#                                 m.vibrate(ev.key - K_KP0)
#         except KeyboardInterrupt:
#             pass
#         finally:
#             m.disconnect()
#     #否则是分析数据
#     else:
#         from sklearn.externals import joblib
#         model=joblib.load('KNN')
#         emg=[]
#         imu=[]
#         while True:
#              emg,imu = getGestureData(m)
#              if emg==10000:
#                  break
#              np.save('emg',emg)
#              np.save('imu',imu)
#              feture=fetureGet(emg,imu)
#              r=model.predict([feture])
#              print(r)