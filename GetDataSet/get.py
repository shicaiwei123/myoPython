import os
import sys
sys.path.append(os.path.pardir)
sys.path.append(os.path.curdir)
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
import argparse
import redis
import json
import logging

import xlrd
import xlwt
from xlutils.copy import copy
from datetime import date

import shutil
r = redis.Redis(host="127.0.0.1")


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
            if len(emgRightData) == 0 or len(imuRightData) == 0:
                continue
            emgRightData, imuRightData = normalized(emgRightData, imuRightData)
            featureOne = featureGet(emgRightData, imuRightData, divisor=8)
            features.append(featureOne)
        # '''获取存放手势的最后一级，目录'''
        # s = path
        # segPath = s.split('/')
        # lastGesturePath = segPath[len(segPath) - 2]
        # '''目标目录'''
        # dstPath = '../Data/GuestData/one/' + lastGesturePath
        # if os.path.exists(dstPath):
        #     shutil.rmtree(dstPath)
        # shutil.move(path, '../Data/GuestData/one')
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
            if len(emgRightData) == 0 or len(imuRightData) == 0 or len(emgLeftData) == 0 or len(imuLeftData) == 0:
                continue
            emgRightData, imuRightData = normalized(emgRightData, imuRightData)
            emgLeftData, imuLeftData = normalized(emgLeftData, imuLeftData)
            featureTwo = featureGetTwo(emgRightData, imuRightData, emgLeftData, imuLeftData, divisorRight=8, divisorLeft=4)
            features.append(featureTwo)
        '''获取存放手势的最后一级，目录'''
        # s = path
        # segPath = s.split('/')
        # lastGesturePath = segPath[len(segPath) - 2]
        # '''目标目录'''
        # dstPath = '../Data/GuestData/one/' + lastGesturePath
        # if os.path.exists(dstPath):
        #     shutil.rmtree(dstPath)
        # shutil.move(path, '../Data/GuestData/two')
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
    if not debug:
        lastPath = currutPath
    else:
        lastPath = os.path.pardir

    logging.error(lastPath)
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
        if not debug:
            r.publish("adjust", json.dumps({"type": "adjust", "data": gestureCounter}))
        print(gestureCounter)
        # if emgRight == 10000:
        if gestureCounter >= DataNumber:
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


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--word', help="adjust the world", default="")
    parser.add_argument('-n', help="adjust count", default=10, type=int)
    parser.add_argument('--hand', help="one hand or two", default=1, type=int)
    return parser.parse_args()


def getMonAndDay():
    today = date.today()
    return str(today.month) + 'm' + str(today.day) + 'd'


class excelutil(object):
    """docstring for excelutil"""

    def __init__(self, fileName):
        super(excelutil, self).__init__()
        self.fileName = fileName
        self.readExcel(fileName)

    def readExcel(self, fileName):
        if not os.path.exists(fileName):
            fileExcel = xlwt.Workbook()
            fileExcel.add_sheet(getMonAndDay())
            fileExcel.save(self.fileName)

        self.rbdata = xlrd.open_workbook(self.fileName)
        self.wbdata = copy(self.rbdata)
        self.setCurrentTableByIndex(0)

    def getcolLength(self):
        data = xlrd.open_workbook(self.fileName)
        table = data.sheet_by_index(0)  # 一个excle可能有多个sheet
        firstCol = table.col_values(0)
        colLength = len(firstCol)
        return colLength

    def setCurrentTableByIndex(self, index):
        self.rbtable = self.rbdata.sheet_by_index(index)
        self.wbtable = self.wbdata.get_sheet(index)

    def setCurrentTableByName(self, sheetName):
        sheetNames = self.rbdata.sheet_names()
        tmpIndex = 0
        for x in range(0, len(sheetNames)):
            if sheetNames[x] == sheetName:
                tmpIndex = x
        self.wbtable = self.wbdata.get_sheet(tmpIndex)
        self.rbtable = self.rbdata.sheet_by_name(sheetName)

    def getValues(self, col, row):
        if self.rbtable == None:
            return 'current rbtable is null'
        # 这个值是rbtable 可能和wbtable值不一样(setValues 没有保存值就不一样) saveExcel（）保存一下就会更新
        return self.rbtable.cell(row, col).value

    def setValues(self, col, row, value):
        self.wbtable.write(row, col, value)

    def addSheet(self, sheetName, new=False):  # new = true 有重名的加一个时间后缀 强制创建新的
        isexist = False
        for name in self.rbdata.sheet_names():
            if name == sheetName:
                if new:
                    sheetName = sheetName + str(time.time())
                isexist = True
        if new or not isexist:
            self.wbdata.add_sheet(sheetName)
        self.saveExcel()
        self.setCurrentTableByName(sheetName)

    # self.setCurrentTableByName(0)

    def saveExcel(self):
        self.wbdata.save(self.fileName)


def addXls(gestureName='', xlsPath=''):
    '''
    如果一个数据不存在于数据集中，则扩充数据集
    为了防止额之前的数据冲突，扩充数据集的标号是从当前存在的数据长度加上10000而得到
    :param gestureName: 扩充的手势名字
    :param xlsPath: 数据集xls表格所在地方
    :return: 返回新数据的label
    '''
    excle = excelutil(xlsPath)
    length = excle.getcolLength()
    gestureLabel = 10000 + length
    gestureRow = length
    excle.setValues(0, gestureRow, gestureLabel)
    excle.setValues(1, gestureRow, gestureName)
    excle.saveExcel()
    return gestureLabel


if __name__ == '__main__':
    """
    用于用户进行自校正
    输入是用户的自定义数据和初始数据，
    """
    debug = False
    # lastPath = os.getcwd()  # 获取上一层目录路径
    lastPath = os.pardir
    # 运行需要在主目录下运行
    gestureDataPath = os.path.join(lastPath, 'dataSheet.xlsx')
    dataDict = excelToDict(gestureDataPath)
    if not debug:
        args = parse()
        if args.word != "":
            # 使用了命令行作为参数
            if args.hand != 1 and args.hand != 2:
                sys.exit()
            handNumber = args.hand
            fileName = args.word
            dataNumber = args.n
            r.publish("adjust", json.dumps({"type": "adjust", "data": "正在连接手环"}))
            myo = myoData.init()
            r.publish("adjust", json.dumps({"type": "adjust", "data": "开始采集"}))
            getDataSet(handNumber, fileName, dataNumber, myo)
        else:
            r.publish("adjust", json.dumps({"type": "adjust", "data": "正在连接手环"}))
            myo = myoData.init()

    else:
        myo = myoData.init()
    while True:
        print("采集单手手势输入1，双手手势输入2：\t")
        handNumber = int(input())
        print("请输入要采集的手势名称：\t")
        fileName = input()
        print("请输入要采集手势的采集数目：\t")
        dataNumber = int(input())
        time.sleep(1)
        print("开始采集\t")
        getDataSet(handNumber, fileName, dataNumber, myo)
        print('是否继续采集数据，是则输入y，否则输入n')
        flag = input()
        if flag == 'n':
            break
    if not debug:
        r.publish("adjust", json.dumps({"type": "adjust", "data": "开始训练"}))
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
                label = addXls(gestureName, gestureDataPath)
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
            # initOnePath = lastPath + '/Data/allDataOne14/'
            # initOneFeature, initOneLabel = getInitData(initOnePath)
            '''读取上次缓存的数据当做此次增加数据的基础数据'''
            backupNumber = getFloderNumber(lastPath + '/Backup/')
            backupPath = lastPath + '/Backup/' + str(backupNumber) + '/GetDataSet'
            initOneFeatureOldPath = backupPath + '/oneFeature.npy'
            initOneLabelOldPath = backupPath + '/oneLabel.npy'
            initOneFeatureOld, initOneLabelOld = getNpyData(initOneFeatureOldPath, initOneLabelOldPath)

            initOneFeatureNewPath = backupPath + '/oneFeatureCache.npy'
            initOneLabelNewPath = backupPath + '/oneLabelCache.npy'
            initOneFeatureNew, initOneLabelNew = getNpyData(initOneFeatureNewPath, initOneLabelNewPath)
            '''新旧的都要读出来'''
            initOneFeature = initOneFeatureOld + initOneFeatureNew
            initOneLabel = initOneLabelOld + initOneLabelNew

            '''加0是方便读取，使用时候不带0'''
            saveNpyDataOne(initOneFeature, initOneLabel, flag=1)
        saveNpyDataOne(features, labels)
        oneFeature = features + initOneFeature
        oneLabel = labels + initOneLabel
        modelOne, accuracyOne = getModel(oneFeature, oneLabel, 0.2)
        joblib.dump(modelOne, 'modelOne')
        print(accuracyOne)
        logging.error(accuracyOne)
        if not debug:
            r.publish("adjust", json.dumps({"type": "adjust", "data": "训练完成"}))

    if gestureTwoNumber != 0:
        features = []
        labels = []
        gestureTwoName = os.listdir(guestTwoPath)
        for i in range(gestureTwoNumber):
            gestureName = gestureTwoName[i]
            label = getKey(dataDict, gestureName)
            if label == None:
                label = addXls(gestureName, gestureDataPath)
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
            # initTwoPath = lastPath + '/Data/allDataTwo11/'
            # initTwoFeature, initTwoLabel = getInitData(initTwoPath)
            '''读取上次缓存的数据当做此次增加数据的基础数据'''
            backupNumber = getFloderNumber(lastPath + '/Backup/')
            backupPath = lastPath + '/Backup/' + str(backupNumber) + '/GetDataSet'
            initTwoFeatureOldPath = backupPath + '/twoFeature.npy'
            initTwoLabelOldPath = backupPath + '/twoLabel.npy'
            initTwoFeatureOld, initTwoLabelOld = getNpyData(initTwoFeatureOldPath, initTwoLabelOldPath)

            initTwoFeatureNewPath = backupPath + '/twoFeatureCache.npy'
            initTwoLabelNewPath = backupPath + '/twoLabelCache.npy'
            initTwoFeatureNew, initTwoLabelNew = getNpyData(initTwoFeatureNewPath, initTwoLabelNewPath)
            initTwoFeature = initTwoFeatureOld + initTwoFeatureNew
            initTwoLabel = initTwoLabelOld + initTwoLabelNew
            '''加0是方便读取，使用时候不带0'''
            saveNpyDataTwo(initTwoFeature, initTwoLabel, flag=1)

        saveNpyDataTwo(features, labels)
        twoFeature = features + initTwoFeature
        twoLabel = labels + initTwoLabel
        modelTwo, accuracyTwo = getModel(twoFeature, twoLabel, 0.2)
        joblib.dump(modelTwo, 'modelTwo')
        print(accuracyTwo)
        logging.error(accuracyTwo)
        if not debug:
            r.publish("adjust", json.dumps({"type": "adjust", "data": "训练完成"}))
