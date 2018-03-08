# -*- coding: utf-8 -*-
#一些常用的数据处理的函数
#数据储存
#数据特征提取

import numpy as np
import  xlwt

def testXlwt(file='new.xls', dataArray=[]):
    book = xlwt.Workbook()  # 创建一个Excel
    sheet1 = book.add_sheet('hello')  # 在其中创建一个名为hello的sheet
    for i in range(len(dataArray)):  # 行数
        for j in range(len(dataArray[i])):  # 列数
            sheet1.write(i, j, dataArray[i][j])
    book.save(file)  # 创建保存文件


def fetureGet(emgData,imuData):
    #初始参数
    frq=50    #频率50Hz
    #数据预处理，归一化，无量纲化
    #转成数组
    emgData=np.array(emgData)
    imuData=np.array(imuData)
    # emgRow=emgData.size/8
    # imuRow=imuData.size/6
    accX=imuData[:,0]
    accY=imuData[:,1]
    accZ=imuData[:,2]
    gcoX=imuData[:,3]
    gcoY=imuData[:,4]
    gcoZ=imuData[:,5]
    emg1=emgData[:,0]
    emg2 = emgData[:, 1]
    emg3 = emgData[:, 2]
    emg4 = emgData[:, 3]
    emg5 = emgData[:, 4]
    emg6 = emgData[:, 5]
    emg7 = emgData[:, 6]
    emg8 = emgData[:, 7]
    acc=np.sqrt(accX**2+accY**2+accZ**2)



    #特征提取
    # 了解一下各个参数的物理意义呢？这样就可以转换
    #是不是某一类的特征多，他就会占据主要地位，就算其他变量很有用，影响也会被消除
    diffAccX=np.diff(accX)
    diffAccY=np.diff(accY)
    diffAccZ=np.diff(accZ)
    gco=np.sqrt(gcoX**2+gcoY**2+gcoZ**2)
    diffGcoX=np.diff(gcoX)
    diffGcoY=np.diff(gcoY)
    diffGcoZ=np.diff(gcoZ)
    meanAccX=np.mean(accX)
    meanAccY=np.mean(accY)
    meanAccZ=np.mean(accZ)
    rmsAccX=np.sqrt(np.mean(accX**2))
    integralAccX=np.sum(accX)*1/frq
    integralAccY=np.sum(accY)*1/frq
    integralAccZ=np.sum(accZ)*1/frq
    rangeAccX=np.max(accX)-np.min(accX)
    rangeAccY=np.max(accY)-np.min(accY)
    meanEmg1=np.mean(emg1)
    meanEmg2 = np.mean(emg2)
    meanEmg3 = np.mean(emg3)
    meanEmg4 = np.mean(emg4)
    meanEmg5 = np.mean(emg5)
    meanEmg6 = np.mean(emg6)
    meanEmg7 = np.mean(emg7)
    meanEmg8 = np.mean(emg8)
    feature=[]
    feature.append(meanAccX);feature.append(meanAccY);feature.append(meanAccZ)
    feature.append(rmsAccX)
    feature.append(integralAccX);feature.append(integralAccY);feature.append(integralAccZ)
    feature.append(rangeAccX);feature.append(rangeAccY)
    feature.append(meanEmg1)
    feature.append(meanEmg2)
    feature.append(meanEmg3)
    feature.append(meanEmg4)
    feature.append(meanEmg5)
    feature.append(meanEmg6)
    feature.append(meanEmg7)
    feature.append(meanEmg8)
    return feature





