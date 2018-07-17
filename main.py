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
import json
import argparse
import logging

debug = False

logging.basicConfig(level=logging.INFO)

if not debug:
    import redis
    r = redis.Redis(host="127.0.0.1")
# speaker = xf_speech()    # 在minnowboard板子上无需设置端口号，默认'/dev/ttyS4'
    speaker = xf_speech('/dev/ttyUSB0')

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
    控制开始识别和结束识别
    控制句子表达的完成
    控制一句话中单词的删除
    :param model: 模型
    :param data: 特征
    :return:
    """

    t1 = time.time()
    global isFinish
    global dataDict
    global isRecognize
    global finishNumber
    global deleteNumber
    result = model.predict(data)
    result = int(result)

    print(result)

    logging.info(result)

    t2 = time.time()
    isFinish = True
    '''判定手语识别的开始和结束'''
    '''如果还没有开始识别那么就检测识别标志，开始识别后就检测结束标志'''
    if not isRecognize:
        if not debug:
            r.publish("log", json.dumps({"type": "mainLog", "data": "等待开始信号, 当前识别手势编号：" + str(result)}))
    if not isRecognize:
        if result == 402:
            deleteNumber = deleteNumber + 1
        else:
            deleteNumber = 0
        if not debug:
            r.publish("log", json.dumps({"type": "mainLog", "data": "已接收到" + str(deleteNumber) + "/2" + "个开始信号"}))
    else:
        if result==401:
            finishNumber=finishNumber+1
        else:
            finishNumber=0

    '''判断，因为不可能同时发生，所以可以独立进行判断'''
    '''状态更新后，数据清零'''
    if deleteNumber == 2:
        isRecognize = True
        deleteNumber = 0

        outCache.clear()
        print('开始识别')
        if not debug:
            r.publish("log", json.dumps({"type": "mainLog", "data": "开始识别"}))
        logging.info('开始识别')

    if finishNumber == 2:
        isRecognize = False
        finishNumber = 0
        logging.info('结束识别')
        if not debug:
            r.publish("log", json.dumps({"type": "mainLog", "data": "结束识别"}))
    """
    401是完成
    402是删除
    其余是数据缓存
    """
    if isRecognize:
        if (result == 402):
            outCache.delete()
            if outCache.size != 0:
                out = outCache.getCache()
                # list->str
                output_str = "".join(out)
                # speaker.speech_sy(str)
                if not debug:
                    r.publish("gesture", json.dumps({"type":"incomplete", "data":output_str}))
                    r.publish("log", json.dumps({"type": "mainLog", "data": "识别结果: " + output_str}))
                # ShowWebSocket.put_data("2", str)
                logging.info(output_str)  # 输出结果
                outCache.clear()
            # else:
                # r.publish("gesture", json.dumps({"type": "incomplete", "data": ""}))
        elif result == 401:
            out = outCache.getCache()
            output_str = "".join(out)
            if not debug:
                speaker.speech_sy(output_str)
            # ShowWebSocket.put_data("1", str)
            if not debug:
                r.publish("gesture", json.dumps({"type":"complete", "data":output_str}))
                r.publish("log", json.dumps({"type": "mainLog", "data": "识别结果: " + output_str}))
            logging.info(output_str)  # 输出结果
            outCache.clear()
        else:
            out = dataDict[result]
            outCache.update(out)
            logging.info(t2 - t1)  # 测试识别时间
            # out = outCache.getCache()
            output_str = "".join(out)
            # speaker.speech_sy(str)
            # ShowWebSocket.put_data("1", str)
            if not debug:
                r.publish("gesture", json.dumps({"type":"incomplete", "data":"".join(outCache.getCache())}))
                r.publish("log", json.dumps({"type": "mainLog", "data": "识别结果: " + output_str}))
            logging.info(output_str)  # 输出结果


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--new", help="use new model", action="store_true")
    return parser.parse_args()


if __name__ == '__main__':
    # 解析命令行参数
    global debug
    if not debug:
        options = parse_arg()
    
    if not debug:
        r.publish('log', json.dumps({"type": "mainLog", "data": "正在连接手环"}))
    m = myoData.init()
    threads = []
    guestModel = ['modelOne', 'modelTwo']
    parantPath = os.getcwd()
    '''判断是否是双手的flag'''
    isTwo = False
    '''判断是否使用新模型'''
    isNew = False
    '''判断是否使用开始手语识别'''
    '''连续统计到两次删除就是开始一次手语识别，否则就是休息模式'''
    '''在手语识别过程中连续统计到两次完成就是退出当前的手语识别'''
    deleteNumber = 0
    finishNumber = 0
    isRecognize = False
    '''如果存在校正模型则询问是否采用校正模型'''
    currentPath = os.getcwd()
    if not debug:
        if os.path.exists(os.path.join(currentPath, 'GetDataSet/model0ne')) or os.path.exists(os.path.join(currentPath, 'GetDataSet/modelTwo')):
            logging.error(options.new)
            if options.new:
                isNew = True
            else:
                isNew = False
    else:
        if os.path.exists(os.path.join(currentPath, 'GetDataSet/model0ne')) or os.path.exists(os.path.join(currentPath, 'GetDataSet/modelTwo')):
            print('是否采用校正模型?是则输入y，若没有或不采用否则输入n')
            flag = input()
            if flag == 'n':
                isNew = False
            elif flag == 'y':
                isNew = True
            else:
                print('error input')
    if not debug:
        logging.error(isNew)
        if isNew:
            r.publish('log', json.dumps({"type": "mainLog", "data": "使用新模型, 等待开始信号"}))
        else:
            r.publish('log', json.dumps({"type": "mainLog", "data": "使用原有模型, 等待开始信号"}))
    # 导入字典数据，后期译码使用
    dataDict = excelToDict('dataSheet.xlsx')
    isFinish = False     # isFinsh 是线程锁
    outCache = DataCache()
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
            feture = featureGetTwo(emgRight, imuRight, emgLeft, imuLeft, divisorRight=8, divisorLeft=4)
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
    if not debug:
        r.publish("log", json.dumps({"type": "mainLog", "data": "已断开手环连接"}))
    # 识别
