from getData.getData import *
from myoAnalysis import *
from voice.speech import xf_speech

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

if __name__ == '__main__':

    m = init()
    # shifoubaocunshuju
    isSave = False
    # 导入模型
    isTwo = False
    # 如果是存储数据
    if isSave:
        # 右手
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
        try:
            while True:
                # emg, imu, emg_raw = getOnceData(m)
                emgRight, imuRight, emgRightAll, imuRightAll, \
                    emgLeft, imuLeft, emgLeftAll, imuLeftAll, \
                    engeryAll, engerySeg = getGestureData(m)
                gestureCounter = gestureCounter + 1
                print(gestureCounter)
                if emgRight == 10000:
                    fileName='wscData2'
                    gestureName = '是'
                    engeryDataSeg = engeryDataSeg + [[gestureCounter - 1]]
                    saveExcle(fileName+'/oneFinger/' + gestureName + '/emgDataRight.xls', emgRightData)
                    saveExcle(fileName+'/oneFinger/' + gestureName + '/imuDataRight.xls', imuRightData)
                    saveExcle(fileName+'/oneFinger/' + gestureName + '/emgDataRightAll.xls', emgRightDataAll)
                    saveExcle(fileName+'/oneFinger/' + gestureName + '/imuDataRightAll.xls', imuRightDataAll)

                    saveExcle(fileName+'/oneFinger/' + gestureName + '/emgDataLeft.xls', emgLeftData)
                    saveExcle(fileName+'/oneFinger/' + gestureName + '/imuDataLeft.xls', imuLeftData)
                    saveExcle(fileName+'/oneFinger/' + gestureName + '/emgDataLeftAll.xls', emgLeftDataAll)
                    saveExcle(fileName+'/oneFinger/' + gestureName + '/imuDataLeftAll.xls', imuLeftDataAll)

                    saveExcle(fileName+'/oneFinger/' + gestureName + '/engeryDataAll.xls', engeryDataAll)
                    saveExcle(fileName+'/oneFinger/' + gestureName + '/engeryDataSeg.xls', engeryDataSeg)
                    # saveExcle('wscData/oneFinger/'+gestureName+'/thresholdData.xls', threshold)
                    raise KeyboardInterrupt()
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

        except KeyboardInterrupt:
            pass
        finally:
            m.disconnect()
    # 否则是分析数据
    else:
        from sklearn.externals import joblib
        import threading
        import queue
        import time

        # 导入字典数据，后期译码使用
        dataDict = excelToDict('dataSheet.xlsx')
        # 预测函数，用于多线程的回调
        # isFinsh 是线程锁
        isFinish = False

        def predict(model, data):
            t1 = time.time()
            global isFinish
            global dataDict
            result = model.predict(data)
            result = int(result)
            t2 = time.time()
            isFinish = True
            out = dataDict[result]
            # speaker.speech_sy(out)
            print(t2 - t1)  # 测试识别时间
            print(out)  # 输出结果
        # 导入模型
        threads = []
        modelOne = joblib.load('SVM3One')
        modelTwo = joblib.load('SVM3Two')
        emg = []
        imu = []
        fetureCache = queue.Queue(10)
        while True:
            emgRight, imuRight, emgRightAll, imuRightAll, \
                emgLeft, imuLeft, emgLeftAll, imuLeftAll, \
                engeryAll, engerySeg = getGestureData(m)
            if emgRight == 10000:
                break
            imuArray = np.array(imuLeft)
            gyo = imuArray[:, 3:6]
            # gyo=np.where(gyo>10)
            gyoLen=len(gyo)
            print(gyoLen)
            gyoE = gyoEngery(gyo)/gyoLen
            print(gyoE)
            if gyoE > 50:
                # print(gyoE)
                isTwo = True
            # 归一化
            emgRightMax = np.max(np.max(emgRight))
            imuRightMax = np.max(np.max(imuRight))
            imuRightMin = np.min(np.min(imuRight))
            emgRight = (emgRight) / emgRightMax
            imuRight = (imuRight - imuRightMin) / (imuRightMax - imuRightMin)

            # 左手
            if isTwo:
                emgLeftMax = np.max(np.max(emgLeft))
                imuLeftMax = np.max(np.max(imuLeft))
                imuLeftMin = np.min(np.min(imuLeft))
                emgLeft = (emgLeft) / emgLeftMax
                imuLeft = (imuLeft - imuLeftMin) / (imuLeftMax - imuLeftMin)

            # 特征提取
            if isTwo:
                feture = featureGetTwo(emgRight, imuRight, emgLeft, imuLeft,divisor=8)
                # 数据缓存
                fetureCache.put([feture])
                t1 = threading.Thread(target=predict, args=(modelTwo, fetureCache.get(),))
                t1.start()
            else:
                feture = featureGet(emgRight, imuRight, divisor=4)
                # 数据缓存
                fetureCache.put([feture])
                t1 = threading.Thread(target=predict, args=(modelOne, fetureCache.get(),))
                t1.start()
            isTwo = False
        m.disconnect()
            # 识别
