import getData.getData as myoData
from myoAnalysis import featureGet, featureGetTwo
from myoAnalysis import excelToDict
from myoAnalysis import normalized
from myoAnalysis import DataCache
from sklearn.externals import joblib
import numpy as np
import threading
import queue
import time
import os
from voice.speech import xf_speech
from Server.server import ShowWebSocket
import redis
import json

r = redis.Redis(host="127.0.0.1")
# speaker = xf_speech()    # 在minnowboard板子上无需设置端口号，默认'/dev/ttyS4'
# speaker = xf_speech('/dev/ttyUSB0')

# isSave取True时时存储数据，取False时时分析数据
# 代码逻辑
"""
代码逻辑
    isSave控制是识别还是采集数据
    isTwo控制是单手还是双手，两个用的两个不同的模型来提高识别的准确度问题
    isTwo的判断通过检测一次手势中的左手的gyo能量来判断，高于阈值则认为是双手
    收集到数据之后，缓存，开启双线程进行识别
"""


def predict(model, data):
    """
    利用模型进行识别，以及进行一些基本的控制
    :param model: 模型
    :param data: 特征
    :return:
    """

    t1 = time.time()
    global isFinish
    global dataDict
    result = model.predict(data)
    result = int(result)
    t2 = time.time()
    isFinish = True
    """
    400和401是完成
    402是删除
    其余是数据缓存
    """
    if (result == 402):
        outCache.delete()
        if outCache.size != 0:
            out = outCache.getCache()
            # list->str
            str = "".join(out)
            r.publish("gesture", json.dumps({"type":"incomplete", "data":str}))
            # ShowWebSocket.put_data("2", str)
            print(str)  # 输出结果
        else:
            r.publish("gesture", json.dumps({"type":"incomplete", "data":""}))
    elif (result == 400) or (result == 401):
        out = outCache.getCache()
        str = "".join(out)
        # speaker.speech_sy(str)
        # ShowWebSocket.put_data("1", str)
        r.publish("gesture", json.dumps({"type":"complete", "data":str}))
        print(str)  # 输出结果
        outCache.clear()
    else:
        out = dataDict[result]
        outCache.update(out)
        print(t2 - t1)  # 测试识别时间
        # out = outCache.getCache()
        str = "".join(out)
        # speaker.speech_sy(str)
        # ShowWebSocket.put_data("1", str)
        r.publish("gesture", json.dumps({"type":"incomplete", "data":"".join(outCache.getCache())}))
        print(str)  # 输出结果


if __name__ == '__main__':
    # 去做准确率测试
    m = myoData.init()
    threads = []
    guestModel = ['modelOne', 'modelTwo']
    parantPath = os.getcwd()
    isTwo = False
    print('isNew?')
    a = input()
    if a == 'y':
        isNew = True
    if a == 'n':
        isNew = False

    # 导入字典数据，后期译码使用
    dataDict = excelToDict('dataSheet.xlsx')
    isFinish = False     # isFinsh 是线程锁
    outCache = DataCache()
    outCache.__init__()
    # 导入模型
    # 如果存在客户自定义模型则导入，不然导入默认模型
    gusetModelPath = 'GetDataSet'
    guestModelContext = os.listdir(gusetModelPath)
    if guestModel[0] in guestModelContext and isNew:
        modelPath = 'GetDataSet/' + guestModel[0]
        modelOne = joblib.load(modelPath)
    else:
        modelOne = joblib.load('SVM3One')

    if guestModel[1] in guestModelContext and isNew:
        modelPath = 'GetDataSet/' + guestModel[1]
        modelTwo = joblib.load(modelPath)
    else:
        modelTwo = joblib.load('SVM3Two')

    emg = []
    imu = []
    fetureCache = queue.Queue(10)
    while True:
        emgRight, imuRight, emgRightAll, imuRightAll, \
            emgLeft, imuLeft, emgLeftAll, imuLeftAll, \
            engeryAll, engerySeg = myoData.getGestureData(m)
        if emgRight == 10000:
            break
        if len(emgRight) < 30:
            continue
        # 判断是否为双手
        imuArray = np.array(imuLeft)
        gyo = imuArray[:, 3:6]
        # gyo=np.where(gyo>10)
        gyoLen = len(gyo)
        # print(gyoLen)
        gyoE = myoData.gyoEngery(gyo) / gyoLen
        # print(gyoE)
        if gyoE > 50:
            # print(gyoE)
            isTwo = True
        # 归一化
        emgRight, imuRight = normalized(emgRight, imuRight)
        # 左手
        if isTwo:
            emgLeft, imuLeft = normalized(emgLeft, imuLeft)
        # 特征提取
        if isTwo:
            feture = featureGetTwo(emgRight, imuRight, emgLeft, imuLeft, divisor=4)
            # 数据缓存
            fetureCache.put([feture])
            t1 = threading.Thread(target=predict, args=(modelTwo, fetureCache.get(),))
            t1.start()
        else:
            feture = featureGet(emgRight, imuRight, divisor=8)
            # 数据缓存
            fetureCache.put([feture])
            t1 = threading.Thread(target=predict, args=(modelOne, fetureCache.get(),))
            t1.start()
        isTwo = False
    m.disconnect()
    # 识别
