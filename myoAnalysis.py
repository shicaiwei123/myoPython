# -*- coding: utf-8 -*-
#一些常用的数据处理的函数
#数据储存
#数据特征提取

import numpy as np
import  math

def ZCR(data):
    # 输入是numpy的一维数组
    # 输出是过零率
    zcrSum=0
    len=np.size(data)
    for i in range(len):
        if i>=1:
            result=np.abs(np.sign(data[i])-np.sign(data[i-1]))
            zcrSum=zcrSum+result
    return zcrSum

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
    #差分
    diffAccX=np.diff(accX)
    diffAccY=np.diff(accY)
    diffAccZ=np.diff(accZ)
    gco=np.sqrt(gcoX**2+gcoY**2+gcoZ**2)
    diffGcoX=np.diff(gcoX)
    diffGcoY=np.diff(gcoY)
    diffGcoZ=np.diff(gcoZ)
    #均值
    meanAccX=np.mean(accX)
    meanAccY=np.mean(accY)
    meanAccZ=np.mean(accZ)
    meanGcoX=np.mean(np.abs(gcoX))
    meanGcoY=np.mean(np.abs(gcoY))
    meanGcoZ=np.mean(np.abs(gcoZ))
    meanDiffAccX=np.mean(np.abs(diffAccX))
    meanDiffAccY = np.mean(np.abs(diffAccY))
    meanDiffAccZ = np.mean(np.abs(diffAccZ))
    meanDiffGcoX=np.mean(np.abs(diffGcoX))
    meanDiffGcoY = np.mean(np.abs(diffGcoY))
    meanDiffGcoZ = np.mean(np.abs(diffGcoZ))
    #均方值
    rmsAccX=np.sqrt(np.mean(accX**2))
    rmsAccY=np.sqrt(np.mean(accY**2))
    rmsAccZ=np.sqrt(np.mean(accZ**2))
    rmsAcc=np.sqrt(np.mean(acc**2))
    rmsGcoX=np.sqrt(np.mean(gcoX**2))
    rmsGcoY=np.sqrt(np.mean(gcoY**2))
    rmsGcoZ=np.sqrt(np.mean(gcoZ**2))
    #积分
    integralAccX=np.sum(accX)*1/frq
    integralAccY=np.sum(accY)*1/frq
    integralAccZ=np.sum(accZ)*1/frq
    #范围
    rangeAccX=np.max(accX)-np.min(accX)
    rangeAccY=np.max(accY)-np.min(accY)
    rangeGcoX=np.max(gcoX)-np.min(gcoX)
    rangeGcoY=np.max(gcoX)-np.min(gcoY)
    rangeGcoZ=np.max(gcoX)-np.min(gcoZ)
    #过零率
    gcoXZCR=ZCR(gcoX)
    gcoYZCR=ZCR(gcoY)
    gcoZZCR=ZCR(gcoZ)
    #均值
    meanEmg1=np.mean(emg1)
    meanEmg2 = np.mean(emg2)
    meanEmg3 = np.mean(emg3)
    meanEmg4 = np.mean(emg4)
    meanEmg5 = np.mean(emg5)
    meanEmg6 = np.mean(emg6)
    meanEmg7 = np.mean(emg7)
    meanEmg8 = np.mean(emg8)
    #
    rmsEmg1=np.mean(emg1)
    rmsEmg2 = np.sqrt(np.mean(emg2**2))
    rmsEmg3 = np.sqrt(np.mean(emg3**2))
    rmsEmg4 = np.sqrt(np.mean(emg4**2))
    rmsEmg5 = np.sqrt(np.mean(emg5**2))
    rmsEmg6 = np.sqrt(np.mean(emg6**2))
    rmsEmg7 = np.sqrt(np.mean(emg7**2))
    rmsEmg8 = np.sqrt(np.mean(emg8**2))
    feature=[]
    feature.append(meanAccX);feature.append(meanAccY);feature.append(meanAccZ)
    # feature.append(meanGcoX);feature.append(meanGcoY);feature.append(meanGcoZ)
    feature.append(rmsAccX);feature.append(rmsAccY);feature.append(rmsAccZ)
    feature.append(rmsGcoX);feature.append(rmsGcoY);feature.append(rmsGcoZ)
    feature.append(integralAccX);feature.append(integralAccY);feature.append(integralAccZ)
    feature.append(rangeAccX);feature.append(rangeAccY)
    feature.append(rangeGcoX);feature.append(rangeGcoY);feature.append(rangeGcoZ)
    # feature.append(meanDiffAccX);feature.append(meanDiffAccY);feature.append(meanDiffAccZ)
    # feature.append(meanDiffGcoX);feature.append(meanDiffGcoY);feature.append(meanDiffGcoZ)
    feature.append(gcoXZCR);feature.append(gcoYZCR);feature.append(gcoZZCR)
    feature.append(meanEmg1)
    feature.append(meanEmg2)
    feature.append(meanEmg3)
    feature.append(meanEmg4)
    feature.append(meanEmg5)
    feature.append(meanEmg6)
    feature.append(meanEmg7)
    feature.append(meanEmg8)
    # feature.append(rmsEmg1)
    # feature.append(rmsEmg2)
    # feature.append(rmsEmg3)
    # feature.append(rmsEmg4)
    # feature.append(rmsEmg5)
    # feature.append(rmsEmg6)
    # feature.append(rmsEmg7)
    # feature.append(rmsEmg8)


    #
    #
    # feature.append(meanAccX);feature.append(meanAccY);feature.append(meanAccZ)
    # # feature.append(meanGcoX);feature.append(meanGcoY);feature.append(meanGcoZ)
    # feature.append(rmsAccX);feature.append(rmsAccY);feature.append(rmsAccZ)
    # feature.append(rmsGcoX);feature.append(rmsGcoY);feature.append(rmsGcoZ)
    # feature.append(integralAccX);feature.append(integralAccY);feature.append(integralAccZ)
    # feature.append(rangeAccX);feature.append(rangeAccY)
    # feature.append(rangeGcoX);feature.append(rangeGcoY);feature.append(rangeGcoZ)
    # # feature.append(meanDiffAccX);feature.append(meanDiffAccY);feature.append(meanDiffAccZ)
    # # feature.append(meanDiffGcoX);feature.append(meanDiffGcoY);feature.append(meanDiffGcoZ)
    # feature.append(gcoXZCR);feature.append(gcoYZCR);feature.append(gcoZZCR)
    # feature.append(meanEmg1)
    # feature.append(meanEmg2)
    # feature.append(meanEmg3)
    # feature.append(meanEmg4)
    # feature.append(meanEmg5)
    # feature.append(meanEmg6)
    # feature.append(meanEmg7)
    # feature.append(meanEmg8)
    # feature.append(rmsEmg1)
    # feature.append(rmsEmg2)
    # feature.append(rmsEmg3)
    # feature.append(rmsEmg4)
    # feature.append(rmsEmg5)
    # feature.append(rmsEmg6)
    # feature.append(rmsEmg7)
    # feature.append(rmsEmg8)
    return feature


import  xlwt
#xlwt只能储存float数据
def testXlwt(file='new.xls', dataArray=[]):
    book = xlwt.Workbook()  # 创建一个Excel
    sheet1 = book.add_sheet('hello')  # 在其中创建一个名为hello的sheet
    for i in range(len(dataArray)):  # 行数
        for j in range(len(dataArray[i])):  # 列数
            sheet1.write(i, j, float(dataArray[i][j]))
    book.save(file)  # 创建保存文件




#测试excle文件生成dict且储存
import xlrd
import pickle
#根据名称获取Excel表格中的数据   参数:file：Excel文件路径  colnameindex：表头列名所在行的所以  ，by_name：Sheet1名称
def excelToDict(file,colnameindex=0,by_name=u'Sheet1'):
    data = xlrd.open_workbook(file)
    table = data.sheet_by_name(by_name)
    colnames = table.row_values(colnameindex)
    nrows = table.nrows
    dict = {}
    for rownum in range(0,nrows):
        row = table.row_values(rownum)
        if row:
            keyName = int(row[0])
            value = row[1]
            if isinstance(value ,float):
                value=int(value)
            dict[keyName]=value
    return dict







