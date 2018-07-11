import os
import sys
sys.path.append(os.path.pardir)
import getData.getData as myoData  # 数据接口
from myoAnalysis import saveExcle  # 数据操作
from myoAnalysis import excelToDict
from myoAnalysis import featureGetTwo, featureGet
from myoAnalysis import normalized
from myoAnalysis import getMatFeature
from myoAnalysis import getModel
from myoAnalysis import saveNpyDataOne
from myoAnalysis import saveNpyDataTwo
from myoAnalysis import getNpyData
from myoAnalysis import getFloderNumber
from sklearn.externals import joblib

import numpy as np
import time


def getKey(dict=None, gestureName=None):
    """
    根据value查找字典的key
    :param dict:   字典
    :param gestureName:  字典的value
    :return:  字典valued对应的 key
    """
    keyList = []
    valueList = []
    label = 0
    for key, value in dict.items():
        keyList.append(key)
        valueList.append(value)
    if gestureName in valueList:
        valueIndex = valueList.index(gestureName)
        label = keyList[valueIndex]
    else:
        label = None
        print("no gesture label")
    return label



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
    firstCol = table.col_values(1)
    for i in range(colNumber):
        dataAll.append(table.col_values(i))
    firstCol = [''] + firstCol
    for i, x in enumerate(firstCol):
        if x == '':
            zeroIndex.append(i)
    zeroNumber = len(zeroIndex)
    for i in range(zeroNumber - 1):
        indexLow = zeroIndex[i]
        indexHigh = zeroIndex[i + 1]
        b = np.array(dataAll)
        dataAll = np.array(dataAll)
        data = dataAll[:, indexLow:indexHigh - 1]
        data = np.array(data)
        data = np.transpose(data)
        # print(data)
        # data = np.delete(data, indexHigh - indexLow - 2, 0)
        data = list(data)
        dataCache.append(data)
    return dataCache


def getxlsFeature(path=''):
    """
    获取用户自定义数据的特征，数据存储在xls表格中
    :param path: 要获取的特征的数据路径
    :param handNumber: 要获取手势是单手还是双手，单手1，双手2
    :return: 手势的特征,二维列表
    """
    features = []
    # 判断单手还是双手
    keyWord = ['two', 'Two']
    handNumber = 1
    for word in keyWord:
        if word in path:
            handNumber = 2
    if handNumber == 1:
        emgRightFile = path + 'emgDataRight.xls'
        imuRightFile = path + 'imuDataRight.xls'
        emgRightDataAll = getxlsData(emgRightFile)
        imuRightDataAll = getxlsData(imuRightFile)
        dataNumber = len(emgRightDataAll)
        for i in range(dataNumber):
            emgRightData = emgRightDataAll.pop()  # 三维list弹出二维list
            imuRightData = imuRightDataAll.pop()
            emgRightData = np.array(emgRightData, dtype='float_')
            imuRightData = np.array(imuRightData, dtype='float_')
            emgRightData, imuRightData = normalized(emgRightData, imuRightData)
            featureOne = featureGet(emgRightData, imuRightData, divisor=8)
            features.append(featureOne)
    elif handNumber == 2:
        emgRightFile = path + 'emgDataRight.xls'
        imuRightFile = path + 'imuDataRight.xls'
        emgLeftFile = path + 'emgDataLeft.xls'
        imuLeftFile = path + 'imuDataLeft.xls'
        emgRightDataAll = getxlsData(emgRightFile)
        imuRightDataAll = getxlsData(imuRightFile)
        emgLeftDataAll = getxlsData(emgLeftFile)
        imuLeftDataAll = getxlsData(imuLeftFile)
        dataNumber = len(emgRightDataAll)
        for i in range(dataNumber):
            emgRightData = emgRightDataAll.pop()  # 三维list弹出二维list
            imuRightData = imuRightDataAll.pop()
            emgLeftData = emgLeftDataAll.pop()
            imuLeftData = imuLeftDataAll.pop()
            emgRightData = np.array(emgRightData, dtype='float_')
            imuRightData = np.array(imuRightData, dtype='float_')
            emgLeftData = np.array(emgLeftData, dtype='float_')
            imuLeftData = np.array(imuLeftData, dtype='float_')
            emgRightData, imuRightData = normalized(emgRightData, imuRightData)
            emgLeftData, imuLeftData = normalized(emgLeftData, imuLeftData)
            featureTwo = featureGetTwo(emgRightData, imuRightData, emgLeftData, imuLeftData, divisorRight=8, divisorLeft=4)
            features.append(featureTwo)
    else:
        print('error')
    return features


def getDataSet(HandNumber=1, FileName=None, DataNumber=12, myo=None):
    """
    获取用户自定义的数据并且存储
    :param HandNumber:   采集的手势是单手的还是双手的
    :param FileName:     采集的手势的名字
    :param DataNumber:   采集的手势要采集多少个
    :param myo:   代表一个手环对象
    :return: 没有返回值，直接是存储的数据
    """

    # 初始化
    currutPath = os.getcwd()
    lastPath = os.path.dirname(currutPath)
    m = myo
    if not os.path.exists(lastPath + '/GuestData'):
        os.makedirs(lastPath + '/GuestData')
    # 右手
    floderPath = lastPath + '/GuestData/'
    emgRightData = []  # 一次手势数据
    imuRightData = []  # 一次手势数据
    emgRightDataAll = []  # 所有数据
    imuRightDataAll = []
    # 左手
    emgLeftData = []  # 一次手势数据
    imuLeftData = []  # 一次手势数据
    emgLeftDataAll = []  # 所有数据
    imuLeftDataAll = []
    # 能量
    engeryDataAll = []  # 所有数据
    engeryDataSeg = []  # 一次手势数据
    gestureCounter = 0
    while True:
        emgRight, imuRight, emgRightAll, imuRightAll, \
            emgLeft, imuLeft, emgLeftAll, imuLeftAll, \
            engeryAll, engerySeg = myoData.getGestureData(m)

        gestureCounter = gestureCounter + 1
        print(gestureCounter)
        # if emgRight == 10000:
        if gestureCounter > DataNumber:
            engeryDataSeg = engeryDataSeg + [[gestureCounter - 1]]
            if HandNumber == 1:
                path = floderPath + 'one/' + FileName
                if not os.path.exists(path):
                    os.makedirs(path)
                saveExcle(path + '/emgDataRight.xls', emgRightData)
                saveExcle(path + '/imuDataRight.xls', imuRightData)
                saveExcle(path + '/emgDataRightAll.xls', emgRightDataAll)
                saveExcle(path + '/imuDataRightAll.xls', imuRightDataAll)

                saveExcle(path + '/engeryDataAll.xls', engeryDataAll)
                saveExcle(path + '/engeryDataSeg.xls', engeryDataSeg)

            elif HandNumber == 2:
                path = floderPath + 'two/' + FileName
                if not os.path.exists(path):
                    os.makedirs(path)
                saveExcle(path + '/emgDataRight.xls', emgRightData)
                saveExcle(path + '/imuDataRight.xls', imuRightData)
                saveExcle(path + '/emgDataRightAll.xls', emgRightDataAll)
                saveExcle(path + '/imuDataRightAll.xls', imuRightDataAll)

                saveExcle(path + '/emgDataLeft.xls', emgLeftData)
                saveExcle(path + '/imuDataLeft.xls', imuLeftData)
                saveExcle(path + '/emgDataLeftAll.xls', emgLeftDataAll)
                saveExcle(path + '/imuDataLeftAll.xls', imuLeftDataAll)

                saveExcle(path + '/engeryDataAll.xls', engeryDataAll)
                saveExcle(path + '/engeryDataSeg.xls', engeryDataSeg)
            else:
                print("error")
            break
            m.disconnect()
        # 完善myo断开逻辑

        # 右手
        emgRightData = emgRightData + emgRight + [[0]]
        # print(emg)
        imuRightData = imuRightData + imuRight + [[0]]

        emgRightDataAll = emgRightDataAll + emgRightAll
        imuRightDataAll = imuRightDataAll + imuRightAll
        # 左手
        emgLeftData = emgLeftData + emgLeft + [[0]]
        # print(emg)
        imuLeftData = imuLeftData + imuLeft + [[0]]

        emgLeftDataAll = emgLeftDataAll + emgLeftAll
        imuLeftDataAll = imuLeftDataAll + imuLeftAll
        # 能量
        engeryDataAll = engeryDataAll + engeryAll
        engeryDataSeg = engeryDataSeg + engerySeg + [[0]]


def getInitData(path=None):
    """
    获取初始系统初始话带有的数据
    :param path: 初始化自带数据路径
    :return: 初始化数据的特征和标签，都是二维列表
    """
    labels = []
    features = []
    dirData = os.listdir(path)
    length = len(dirData)  # 数据总数,
    for i in range(1, length):
        file = path + str(i) + '.mat'
        feature, label = getMatFeature(file)
        label = list(label[0])
        features.append(feature)
        labels.append(label)
    return features, labels


if __name__ == '__main__':
    """
    用于用户进行自校正
    输入是用户的自定义数据和初始数据，
    """
    # myo = myoData.init()
    lastPath = os.path.dirname(os.getcwd())  # 获取上一层目录路径
    gestureDataPath = lastPath + '/dataSheet.xlsx'
    dataDict = excelToDict(gestureDataPath)
    # while True:
    #     print("采集单手手势输入1，双手手势输入2：\t")
    #     handNumber = int(input())
    #     print("请输入要采集的手势名称：\t")
    #     fileName = input()
    #     print("请输入要采集手势的采集数目：\t")
    #     dataNumber = int(input())
    #     time.sleep(1)
    #     print("开始采集\t")
    #     getDataSet(handNumber, fileName, dataNumber, myo)
    #     print('是否继续？继续请输入y，否则输入n')
    #     flag = input()
    #     if flag == 'n':
    #         break

    print('开始训练')
    guestOnePath = lastPath + '/GuestData/one/'
    guestTwoPath = lastPath + '/GuestData/two/'
    gestureOneNumber = getFloderNumber(guestOnePath)
    gestureTwoNumber = getFloderNumber(guestTwoPath)

    # 操作单手数据
    if gestureOneNumber != 0:
        features = []
        labels = []
        gestureOneName = os.listdir(guestOnePath)
        for i in range(gestureOneNumber):
            gestureName = gestureOneName[i]
            label = getKey(dataDict, gestureName)
            if label == None:
                continue
            gesturePath = guestOnePath + gestureName + '/'
            gestureFeature = getxlsFeature(gesturePath)
            features = features + gestureFeature
            featureNumber = len(gestureFeature)
            for _ in range(featureNumber):
                labels.append([label])
        '''如果已经存在则直接都去，不然从data文件读取并保存'''
        if os.path.exists('oneFeature.npy'):

            initOneFeature, initOneLabel = getNpyData('oneFeature.npy', 'oneLabel.npy')
            # 读取
        else:
            initOnePath = lastPath + '/Data/allDataOne7/'
            initOneFeature, initOneLabel = getInitData(initOnePath)
            '''加0是方便读取，使用时候不带0'''
            saveNpyDataOne(initOneFeature, initOneLabel, flag=1)
        saveNpyDataOne(features, labels)
        oneFeature = features + initOneFeature
        oneLabel = labels + initOneLabel
        if len(features)<20:
            print('error')
        modelOne, accuracyOne = getModel(oneFeature, oneLabel, 0.2)
        joblib.dump(modelOne, 'modelOne')
        print(accuracyOne)

    if gestureTwoNumber != 0:
        features = []
        labels = []
        gestureTwoName = os.listdir(guestTwoPath)
        for i in range(gestureTwoNumber):
            gestureName = gestureTwoName[i]
            label = getKey(dataDict, gestureName)
            if label == None:
                continue
            gesturePath = guestTwoPath + gestureName + '/'
            gestureFeature = getxlsFeature(gesturePath)
            features = features + gestureFeature
            featureNumber = len(gestureFeature)
            for _ in range(featureNumber):
                labels.append([label])
        '''如果已经存在则直接都去，不然从data文件读取并保存'''
        if os.path.exists('twoFeature.npy'):

            initTwoFeature, initTwoLabel = getNpyData('twoFeature.npy', 'twoLabel.npy')
            # 读取
        else:
            initTwoPath = lastPath + '/Data/allDataTwo5/'
            initTwoFeature, initTwoLabel = getInitData(initTwoPath)
            '''加0是方便读取，使用时候不带0'''
            saveNpyDataTwo(initTwoFeature, initTwoLabel, flag=1)

        saveNpyDataTwo(features, labels)
        twoFeature = features + initTwoFeature
        twoLabel = labels + initTwoLabel
        modelTwo, accuracyTwo = getModel(twoFeature, twoLabel, 0.2)
        joblib.dump(modelTwo, 'modelTwo')
        print(accuracyTwo)
