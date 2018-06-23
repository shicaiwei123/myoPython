import getData.getData as myoData  # 数据接口
from myoAnalysis import saveExcle  # 数据操作
from myoAnalysis import excelToDict
from myoAnalysis import featureGetTwo, featureGet
from myoAnalysis import normalized
from myoAnalysis import getMatFeature
from myoAnalysis import getModel
from sklearn.externals import joblib
import os
import numpy as np


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
        print("no gesture label")
    return label


def getFloderNumber(path=None):
    """
    获取文件夹下文件夹数目
    :param path: 文件夹路径
    :return: 当前路径下文件夹数目
    """
    count = 0
    floderExist = os.path.exists(path)
    if floderExist:
        for fn in os.listdir(path):  # fn 表示的是文件名
            count = count + 1
    return count


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
        import numpy as np
        b = np.array(dataAll)
        dataAll = np.array(dataAll)
        data = dataAll[:, indexLow:indexHigh - 1]
        data = np.array(data)
        data = np.transpose(data)
        data = np.delete(data, indexHigh - indexLow - 2, 0)
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
            featureTwo = featureGetTwo(emgRightData, imuRightData, emgLeftData, imuLeftData, divisor=4)
            features.append(featureTwo)
    else:
        print('error')
    return features


def getDataSet(HandNumber=1, FileName=None, DataNumber=12):
    """
    获取用户自定义的数据并且存储
    :param HandNumber:   采集的手势是单手的还是双手的
    :param FileName:     采集的手势的名字
    :param DataNumber:   采集的手势要采集多少个
    :return: 没有返回值，直接是存储的数据
    """

    # 初始化
    m = myoData.init()
    if not os.path.exists('GuestData'):
        os.makedirs('GuestData')
    # 右手
    floderPath = 'GuestData/'
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


def getInitDaat(path=None):
    """
    获取初始系统初始话带有的数据
    :param path: 初始化自带数据路径
    :return: 初始化数据的特征和标签，都是二维列表
    """
    labels=[]
    features=[]
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
    获取数据
    """
    lastPath = os.path.dirname(os.getcwd()) # 获取上一层目录路径
    gestureDataPath=lastPath+'/dataSheet.xlsx'
    dataDict = excelToDict(gestureDataPath)
    features = []
    labels = []
    # while True:
    #     print("采集单手手势输入1，双手手势输入2：\t")
    #     handNumber = int(input())
    #     print("请输入要采集的手势名称：\t")
    #     fileName = input()
    #     print("请输入要采集手势的采集数目：\t")
    #     dataNumber = int(input())
    #     getDataSet(handNumber, fileName, dataNumber)
    #     print('是否继续？继续请输入y，否则输入n')
    #     flag=input()
    #     if flag=='n':
    #         break


# lable单独保存，后面可能是存一次就训练，也可能采集多次再训练
# 同一个手势采集了多次怎么办？
    # 训练的时候遍历这些文件夹
    # 用户可以选择删除这些文件夹，全部删除，选择删除，虽然我们应该提供更好哦的服务，让用户尽可能不去选择这个功能
    # 训练的模型也可以保存，用户随意选择，加载的时候只从其中一个地方加载
    # 可以恢复出厂设置
    # 读数据，读取我们的和用户的，然后一起训练，我们的就是这样了，全部读入，用户也全部读入，然后训练，或者设置一个比例
    # 接下来是文件操作，数据读取，训练，保存。
    # 天，那还不如就直接做一个app设置。

    guestOnePath = lastPath+'/GuestData/one/'
    guestTwoPath = lastPath+'/GuestData/two/'
    gestureOneNumber = getFloderNumber(guestOnePath)
    gestureTwoNumber = getFloderNumber(guestTwoPath)
    rootOne, oneFileName, file = os.walk(guestOnePath)
    rootTwo, twoFileName, file = os.walk(guestOnePath)
    gestureOneName = rootOne[1]
    gestureTwoName = rootTwo[1]
    # 操作单手数据
    for i in range(gestureOneNumber):
        gestureName = gestureOneName[i]
        label = getKey(dataDict, gestureName)
        gesturePath = guestOnePath + gestureName + '/'
        gestureFeature = getxlsFeature(gesturePath)
        features=features+gestureFeature
        featureNumber = len(gestureFeature)
        for _ in range(featureNumber):
            labels.append([label])

    # 获取系统初始化的单手的数据
    initOnePath = lastPath + '/allDataOne6/'
    initOneFeature, initOneLabel = getInitDaat(initOnePath)
    oneFeature = features + initOneFeature
    oneLabel = labels + initOneLabel
    modelOne,accuracyOne=getModel(oneFeature,oneLabel,0.2)
    joblib.dump(modelOne, 'modelOne')
    print(accuracyOne)

    # 操作双手数据
    for i in range(gestureTwoNumber):
        gestureName = gestureTwoName[i]
        gesturePath = guestOnePath + gestureName + '/'
        gestureFeature = getxlsFeature(gesturePath)
        features = features + gestureFeature
        featureNumber = len(gestureFeature)
        label = getKey(dataDict, gestureName)
        label = list(label)
        for _ in range(featureNumber):
            labels.append(label)
    # 获取初始化双特征并训练
    initTwoPath = lastPath + '/allDataTwo4/'
    initTwoFeature, initTwoLabel = getInitDaat(initTwoPath)
    twoFeature = features + initTwoFeature
    twoLabel = labels + initTwoLabel
    modelTwo,accuracyTwo = getModel(twoFeature, twoLabel,0.2)
    joblib.dump(modelTwo, 'modelTwo')
    print(accuracyTwo)
