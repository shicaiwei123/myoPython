# -*- coding: utf-8 -*-
# 一些常用的数据处理的函数
# 数据储存
# 数据特征提取

import numpy as np
import xlwt
import scipy.io as scio


# xlwt只能储存float数据

def _ZCR(data):
    # 输入是numpy的一维数组
    # 输出是过零率
    zcrSum = 0
    len = np.size(data)
    for i in range(len):
        if i >= 1:
            result = np.abs(np.sign(data[i]) - np.sign(data[i - 1]))
            zcrSum = zcrSum + result
    return zcrSum


def featureGet(emgDataAll, imuDataAll, divisor=8):
    # 初始参数
    """
    获取数据的特征
    :param emgDataAll:  emg数据，可以是list也可以是array
    :param imuDataAll: imu数据，可以是list也可以是array
    :param divisor: 分片数
    :return: 返回特征
    """
    emgDataAll = np.array(emgDataAll)
    imuDataAll = np.array(imuDataAll)
    frq = 50  # 频率50Hz
    lenData = len(emgDataAll[:, 1])
    reminder = np.mod(lenData, divisor)
    lenData = lenData - reminder
    windows = int(lenData / divisor)
    feature = []
    global ddddddd
    for j in range(divisor):
        # 数据预处理，归一化，无量纲化
        # 转成数组
        if j == 2:
            a = 1

        emgData = emgDataAll[0 + j * windows:windows + j * windows, :]
        imuData = imuDataAll[0 + j * windows:windows + j * windows, :]
        accX = imuData[:, 0]
        accY = imuData[:, 1]
        accZ = imuData[:, 2]
        gcoX = imuData[:, 3]
        gcoY = imuData[:, 4]
        gcoZ = imuData[:, 5]
        emg1 = emgData[:, 0]
        emg2 = emgData[:, 1]
        emg3 = emgData[:, 2]
        emg4 = emgData[:, 3]
        emg5 = emgData[:, 4]
        emg6 = emgData[:, 5]
        emg7 = emgData[:, 6]
        emg8 = emgData[:, 7]
        acc = np.sqrt(accX**2 + accY**2 + accZ**2)

        # 特征提取
        # 了解一下各个参数的物理意义呢？这样就可以转换
        # 是不是某一类的特征多，他就会占据主要地位，就算其他变量很有用，影响也会被消除
        # 差分
        diffAccX = np.diff(accX)
        diffAccY = np.diff(accY)
        diffAccZ = np.diff(accZ)
        gco = np.sqrt(gcoX**2 + gcoY**2 + gcoZ**2)
        diffGcoX = np.diff(gcoX)
        diffGcoY = np.diff(gcoY)
        diffGcoZ = np.diff(gcoZ)
        # 均值
        meanAccX = np.mean(accX)
        meanAccY = np.mean(accY)
        meanAccZ = np.mean(accZ)
        meanGcoX = np.mean(np.abs(gcoX))
        meanGcoY = np.mean(np.abs(gcoY))
        meanGcoZ = np.mean(np.abs(gcoZ))
        meanDiffAccX = np.mean(np.abs(diffAccX))
        meanDiffAccY = np.mean(np.abs(diffAccY))
        meanDiffAccZ = np.mean(np.abs(diffAccZ))
        meanDiffGcoX = np.mean(np.abs(diffGcoX))
        meanDiffGcoY = np.mean(np.abs(diffGcoY))
        meanDiffGcoZ = np.mean(np.abs(diffGcoZ))
        # 均方值
        rmsAccX = np.sqrt(np.mean(accX**2))
        rmsAccY = np.sqrt(np.mean(accY**2))
        rmsAccZ = np.sqrt(np.mean(accZ**2))
        rmsAcc = np.sqrt(np.mean(acc**2))
        rmsGcoX = np.sqrt(np.mean(gcoX**2))
        rmsGcoY = np.sqrt(np.mean(gcoY**2))
        rmsGcoZ = np.sqrt(np.mean(gcoZ**2))
        # 积分
        integralAccX = np.sum(accX) * 1 / frq
        integralAccY = np.sum(accY) * 1 / frq
        integralAccZ = np.sum(accZ) * 1 / frq
        # 范围
        rangeAccX = np.max(accX) - np.min(accX)
        rangeAccY = np.max(accY) - np.min(accY)
        rangeGcoX = np.max(gcoX) - np.min(gcoX)
        rangeGcoY = np.max(gcoX) - np.min(gcoY)
        rangeGcoZ = np.max(gcoX) - np.min(gcoZ)
        # 过零率
        gcoXZCR = _ZCR(gcoX)
        gcoYZCR = _ZCR(gcoY)
        gcoZZCR = _ZCR(gcoZ)
        # 均值
        meanEmg1 = np.mean(emg1)
        meanEmg2 = np.mean(emg2)
        meanEmg3 = np.mean(emg3)
        meanEmg4 = np.mean(emg4)
        meanEmg5 = np.mean(emg5)
        meanEmg6 = np.mean(emg6)
        meanEmg7 = np.mean(emg7)
        meanEmg8 = np.mean(emg8)
        # 均方值
        rmsEmg1 = np.mean(emg1)
        rmsEmg2 = np.sqrt(np.mean(emg2**2))
        rmsEmg3 = np.sqrt(np.mean(emg3**2))
        rmsEmg4 = np.sqrt(np.mean(emg4**2))
        rmsEmg5 = np.sqrt(np.mean(emg5**2))
        rmsEmg6 = np.sqrt(np.mean(emg6**2))
        rmsEmg7 = np.sqrt(np.mean(emg7**2))
        rmsEmg8 = np.sqrt(np.mean(emg8**2))
        # 第一次测试，效果还可以
        # feature = []
        # feature.append(meanAccX)
        # feature.append(meanAccY)
        # feature.append(meanAccZ)
        # # feature.append(meanGcoX);feature.append(meanGcoY);feature.append(meanGcoZ)
        # feature.append(rmsAccX)
        # feature.append(rmsAccY)
        # feature.append(rmsAccZ)
        # feature.append(rmsGcoX)
        # feature.append(rmsGcoY)
        # feature.append(rmsGcoZ)
        # feature.append(integralAccX)
        # feature.append(integralAccY)
        # feature.append(integralAccZ)
        # feature.append(rangeAccX)
        # feature.append(rangeAccY)
        # feature.append(rangeGcoX)
        # feature.append(rangeGcoY)
        # feature.append(rangeGcoZ)
        # # feature.append(meanDiffAccX);feature.append(meanDiffAccY);feature.append(meanDiffAccZ)
        # # feature.append(meanDiffGcoX);feature.append(meanDiffGcoY);feature.append(meanDiffGcoZ)
        # feature.append(gcoXZCR)
        # feature.append(gcoYZCR)
        # feature.append(gcoZZCR)
        # feature.append(meanEmg1)
        # feature.append(meanEmg2)
        # feature.append(meanEmg3)
        # feature.append(meanEmg4)
        # feature.append(meanEmg5)
        # feature.append(meanEmg6)
        # feature.append(meanEmg7)
        # feature.append(meanEmg8)
        # # feature.append(rmsEmg1)
        # # feature.append(rmsEmg2)
        # # feature.append(rmsEmg3)
        # # feature.append(rmsEmg4)
        # # feature.append(rmsEmg5)
        # # feature.append(rmsEmg6)
        # # feature.append(rmsEmg7)
        # # feature.append(rmsEmg8)

        test = 2  # 第二类特征，效果又再好了一些
        # feature = []
        # feature.append(meanAccX)
        # feature.append(meanAccY)
        # feature.append(meanAccZ)
        # # feature.append(meanGcoX);feature.append(meanGcoY);feature.append(meanGcoZ)
        # feature.append(rmsAccX)
        # feature.append(rmsAccY)
        # feature.append(rmsAccZ)
        # feature.append(rmsGcoX)
        # feature.append(rmsGcoY)
        # feature.append(rmsGcoZ)
        # feature.append(integralAccX)
        # feature.append(integralAccY)
        # feature.append(integralAccZ)
        # feature.append(rangeAccX)
        # feature.append(rangeAccY)
        # feature.append(rangeGcoX)
        # feature.append(rangeGcoY)
        # feature.append(rangeGcoZ)
        # # feature.append(meanDiffAccX);feature.append(meanDiffAccY);feature.append(meanDiffAccZ)
        # # feature.append(meanDiffGcoX);feature.append(meanDiffGcoY);feature.append(meanDiffGcoZ)
        # feature.append(gcoXZCR)
        # feature.append(gcoYZCR)
        # feature.append(gcoZZCR)
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
        test = 3  # 第三次测试,效果比第二次又好了那么一点点。
        feature.append(meanAccX)
        feature.append(meanAccY)
        feature.append(meanAccZ)
        feature.append(meanGcoX)
        feature.append(meanGcoY)
        feature.append(meanGcoZ)
        feature.append(rmsAccX)
        feature.append(rmsAccY)
        feature.append(rmsAccZ)
        feature.append(rmsGcoX)
        feature.append(rmsGcoY)
        feature.append(rmsGcoZ)
        feature.append(integralAccX)
        feature.append(integralAccY)
        feature.append(integralAccZ)
        feature.append(rangeAccX)
        feature.append(rangeAccY)
        feature.append(rangeGcoX)
        feature.append(rangeGcoY)
        feature.append(rangeGcoZ)
        # feature.append(meanDiffAccX);feature.append(meanDiffAccY);feature.append(meanDiffAccZ)
        # feature.append(meanDiffGcoX);feature.append(meanDiffGcoY);feature.append(meanDiffGcoZ)
        feature.append(gcoXZCR)
        feature.append(gcoYZCR)
        feature.append(gcoZZCR)
        feature.append(meanEmg1)
        feature.append(meanEmg2)
        feature.append(meanEmg3)
        feature.append(meanEmg4)
        feature.append(meanEmg5)
        feature.append(meanEmg6)
        feature.append(meanEmg7)
        feature.append(meanEmg8)
        feature.append(rmsEmg1)
        feature.append(rmsEmg2)
        feature.append(rmsEmg3)
        feature.append(rmsEmg4)
        feature.append(rmsEmg5)
        feature.append(rmsEmg6)
        feature.append(rmsEmg7)
        feature.append(rmsEmg8)
    return feature


def featureGetTwo(emgDataRightAll, imuDataRightAll, emgDataLeftAll, imuDataLeftAll, divisor=4):
    featureRight = featureGet(emgDataRightAll, imuDataRightAll, divisor)
    featureLeft = featureGet(emgDataLeftAll, imuDataLeftAll, divisor)
    featureAll = featureRight + featureLeft
    return featureAll


def saveExcleTwoDimension(file='new.xls', dataArray=[], index=0):
    # index是行偏置
    book = xlwt.Workbook()  # 创建一个Excel
    sheet1 = book.add_sheet('hello')  # 在其中创建一个名为hello的sheet
    for i in range(len(dataArray)):  # 行数
        for j in range(len(dataArray[i])):  # 列数
            sheet1.write(i + index, j, float(dataArray[i][j]))
    book.save(file)  # 创建保存文件
    return index + len(dataArray)


def saveExcle(file='new.xls', dataArray=[], dimensions=2):
    index = 0
    if dimensions == 2:
        saveExcleTwoDimension(file, dataArray)
    else:
        # 此时只考虑三维
        dataNumber = len(dataArray[0])
        for i in range(dataNumber):
            index = saveExcleTwoDimension(file, dataArray[i], index)



# 测试excle文件生成dict且储存
import xlrd
import pickle
# 根据名称获取Excel表格中的数据   参数:file：Excel文件路径  colnameindex：表头列名所在行的所以  ，by_name：Sheet1名称


def excelToDict(file, colnameindex=0, by_name=u'Sheet1'):
    data = xlrd.open_workbook(file)
    table = data.sheet_by_name(by_name)
    colnames = table.row_values(colnameindex)
    nrows = table.nrows
    dict = {}
    for rownum in range(0, nrows):
        row = table.row_values(rownum)
        if row:
            keyName = int(row[0])
            value = row[1]
            if isinstance(value, float):
                value = int(value)
            dict[keyName] = value
    return dict


class DataCache():
    """"""

    def __init__(self, maxCacheSize=100):
        """Constructor"""
        self.cache = []
        self.max_cache_size = maxCacheSize
        self.cacheLength = 0

    def getCache(self):
        """
        根据该键是否存在于缓存当中返回True或者False
        """
        return self.cache

    def update(self, string):
        """
        更新该缓存
        """
        if self.cacheLength > self.max_cache_size:
            print('cache is full')
            return False

        self.cache.append(string)
        self.cacheLength = self.cacheLength + 1

    def delete(self):
        """
        删除具备最早访问日期的输入数据
        """
        if self.cacheLength == 0:
            print('Null')
        else:
            self.cache.pop()
            self.cacheLength = self.cacheLength - 1

    @property
    def size(self):
        """
        返回缓存容量大小
        """
        return self.cacheLength

    def clear(self):
        self.cache = []
        self.cacheLength = 0


def normalized(gestureEmg, gestureImu):
    """
    对数据归一化
    :param gestureEmg:  手语运动的肌电流数据
    :param gestureEmg:  手语运动的惯性传感器数据
    :return:  归一化数据的肌电流，惯性传感器数据
    """
    emgMax = np.max(np.max(gestureEmg))
    imuMax = np.max(np.max(gestureImu))
    imuMin = np.min(np.min(gestureImu))
    emgData = (gestureEmg) / emgMax
    imuData = (gestureImu - imuMin) / (imuMax - imuMin)
    return emgData, imuData


def getMatFeature(file):
    """
    mat数据结构
    包含结构体w
    w包含四个数据，emgData imuData len以及 lables
    len是包含了，但是当时统计错误
    nonZeoLabel是非0数组下标，row是非0数据行数
    读取数据
    :param file:
    :return: 特征和标签
    """
    data = scio.loadmat(file)
    featureOne = []
    featureTwo = []
    w = data['data']
    dataType = w['dataType']
    dataType = dataType[0, 0]
    dataType = dataType[0, 0]
    if dataType == 2:
        emgRight = w['emgRight']
        imuRight = w['imuRight']
        emgRight = emgRight[0, 0]
        imuRight = imuRight[0, 0]
        emgLeft = w['emgLeft']
        imuLeft = w['imuLeft']
        emgLeft = emgLeft[0, 0]
        imuLeft = imuLeft[0, 0]
        labels = w['Lable']
        labels = labels[0, 0]
        len = w['len']
        len = len[0, 0]
        len = len[0, 0]
        row = len
        emgLeft = emgLeft[0:row, :]
        imuLeft = imuLeft[0:row, :]
        emgLeft, imuLeft = normalized(emgLeft, imuLeft)
    else:
        emgRight = w['emgData']
        imuRight = w['imuData']
        emgRight = emgRight[0, 0]
        imuRight = imuRight[0, 0]
        labels = w['lables']
        labels = labels[0, 0]
        len = w['len']
        len = len[0, 0]
        len = len[0, 0]
        row = len * 5
        # 只有一只手的数据，那就将左手设定为0
        emgLeft = 0
        imuLeft = 0
    emgRight = emgRight[0:row, :]
    imuRight = imuRight[0:row, :]

    # 归一化
    emgRight, imuRight = normalized(emgRight, imuRight)
    if dataType == 1:
        featureOne = featureGet(emgRight, imuRight, divisor=8)

    elif dataType == 2:
        featureTwo = featureGetTwo(emgRight, imuRight, emgLeft, imuLeft, divisor=4)
    if featureOne == []:
        return featureTwo, labels
    else:
        return featureOne, labels



def getxlsData(file='*.xls'):
    """
    从xls中获取分段好的数据
    :param file: 存储数据的xls文件
    :return: 分段好的所有数据
    """
    import xlrd
    data = xlrd.open_workbook(file)
    table = data.sheet_by_index(0)  # 一个excle可能有多个sheet
    colNumber = table.ncols
    dataAll = []
    zeroIndex = []
    dataCache = []
    firstCol = table.col_values(0)
    for i in range(colNumber):
        dataAll.append(table.col_values(i))
    firstCol = [0] + firstCol
    for i, x in enumerate(firstCol):
        if x == 0:
            zeroIndex.append(i)
    zeroNumber = len(zeroIndex)
    for i in range(zeroNumber - 1):
        indexLow = zeroIndex[i]
        indexHigh = zeroIndex[i + 1]
        data = dataAll[indexLow + 1:indexHigh]
        dataCache.append(data)
    return dataCache


def getxlsFeature(path=''):
    """
    获取用户自定义数据的特征，数据存储在xls表格中
    :param path: 要获取的特征的数据路径
    :param handNumber: 要获取手势是单手还是双手，单手1，双手2
    :return: 手势的特征
    """
    features=[]
    #判断单手还是双手
    keyWord=['two','Two']
    handNumber=1
    for word in keyWord:
        if word in path:
            handNumber=2
    if handNumber ==1:
        emgRightFile=path+'emgDataRight.xls'
        imuRightFile=path+'imuDataRight.xls'
        emgRightDataAll=getxlsData(emgRightFile)
        imuRightDataAll=getxlsData(imuRightFile)
        dataNumber=len(emgRightDataAll)
        for i in range(dataNumber):
            emgRighData=emgRightDataAll.pop() #三维list弹出二维list
            imuRightData=imuRightDataAll.pop()
            featureOne=featureGet(emgRighData,imuRightData,divisor=8)
            features.append(featureOne)
    elif handNumber ==2:
        emgRightFile=path+'emgDataRight.xls'
        imuRightFile=path+'imuDataRight.xls'
        emgLeftFile=path+'emgDataLeft.xls'
        imuLeftFile=path+'imuDataLeft.xls'
        emgRightDataAll=getxlsData(emgRightFile)
        imuRightDataAll=getxlsData(imuRightFile)
        emgLeftDataAll=getxlsData(emgLeftFile)
        imuLeftDataAll = getxlsData(imuLeftFile)
        dataNumber=len(emgRightDataAll)
        for i in range(dataNumber):
            emgRighData=emgRightDataAll.pop() #三维list弹出二维list
            imuRightData=imuRightDataAll.pop()
            emgLeftData=emgLeftDataAll.pop()
            imuLeftData=imuLeftDataAll.pop()
            featureTwo=featureGetTwo(emgRighData,imuRightData,emgLeftData,imuLeftData,divisor=8)
            features.append(featureTwo)
    else:
        print('error')
    return  features



def getKNN(trainX, trainY):
    from sklearn.neighbors import KNeighborsClassifier as knn
    trainX = np.array(trainX)
    trainY = np.array(trainY)
    model = knn(n_neighbors=1, weights='distance')
    model.fit(trainX, trainY.ravel())
    return model


def getSVM(trainX, trainY):
    from sklearn.svm import SVC
    trainX = np.array(trainX)
    trainY = np.array(trainY)
    model = SVC(kernel='linear', degree=3)
    model.fit(trainX, trainY.ravel())
    return model


if __name__ == '__main__':
    cache = DataCache()
    cache.update('你好')
    cache.delete()
    print(cache.getCache())
