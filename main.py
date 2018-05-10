from getData.getData import *
from myoAnalysis import *
from voice.speech import xf_speech

# speaker = xf_speech()    # 在minnowboard板子上无需设置端口号，默认'/dev/ttyS4'
# speaker = xf_speech('/dev/ttyUSB0')

# isSave取True时时存储数据，取False时时分析数据
if __name__ == '__main__':

    m = init()
    # shifoubaocunshuju
    isSave = True
    # 导入模型

    # 如果是存储数据
    if isSave:
        #右手
        emgRightData = []  # 一次手势数据
        imuRightData = []  # 一次手势数据
        emgRightDataAll = []  # 所有数据
        imuRightDataAll = []
        #左手
        emgLeftData = []  # 一次手势数据
        imuLeftData = []  # 一次手势数据
        emgLeftDataAll = []  # 所有数据
        imuLeftDataAll = []
        #能量
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

                    name = '2'
                    engeryDataSeg = engeryDataSeg + [[gestureCounter - 1]]
                    saveExcle('wscData2/oneFinger/' + name + '/emgRightData.xls', emgRightData)
                    saveExcle('wscData2/oneFinger/' + name + '/imuRightData.xls', imuRightData)
                    saveExcle('wscData2/oneFinger/' + name + '/emgRightDataAll.xls', emgRightDataAll)
                    saveExcle('wscData2/oneFinger/' + name + '/imuRightDataAll.xls', imuRightDataAll)

                    saveExcle('wscData2/oneFinger/' + name + '/emgLeftData.xls', emgLeftData)
                    saveExcle('wscData2/oneFinger/' + name + '/imuLeftData.xls', imuLeftData)
                    saveExcle('wscData2/oneFinger/' + name + '/emgLeftDataAll.xls', emgLeftDataAll)
                    saveExcle('wscData2/oneFinger/' + name + '/imuLeftDataAll.xls', imuLeftDataAll)

                    saveExcle('wscData2/oneFinger/' + name + '/engeryDataAll.xls', engeryDataAll)
                    saveExcle('wscData2/oneFinger/' + name + '/engeryDataSeg.xls', engeryDataSeg)
                    # saveExcle('wscData/oneFinger/'+name+'/thresholdData.xls', threshold)
                    raise KeyboardInterrupt()
                #右手
                emgRightData = emgRightData + emgRight + [[0]]
                # print(emg)
                imuRightData = imuRightData + imuRight + [[0]]

                emgRightDataAll = emgRightDataAll + emgRightAll
                imuRightDataAll = imuRightDataAll + imuRightAll
                #左手
                emgLeftData = emgLeftData + emgLeft + [[0]]
                # print(emg)
                imuLeftData = imuLeftData + imuLeft + [[0]]

                emgLeftDataAll = emgLeftDataAll + emgLeftAll
                imuLeftDataAll = imuLeftDataAll + imuLeftAll
                #能量
                engeryDataAll = engeryDataAll + engeryAll
                engeryDataSeg = engeryDataSeg + engerySeg + [[0]]

        except KeyboardInterrupt:
            pass
        finally:
            pass
            # m.disconnect()
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
        model = joblib.load('KNN30')
        emg = []
        imu = []
        fetureCache = queue.Queue(10)
        while True:
            emg, imu, a, b, c, d, e,F,G,H,i= getGestureData(m)
            if emg == 10000:
                break
            # 归一化
            emgMax = np.max(np.max(emg))
            imuMax = np.max(np.max(imu))
            imuMin = np.min(np.min(imu))
            emg = (emg) / emgMax
            imu = (imu - imuMin) / (imuMax - imuMin)
            # 特征提取
            feture = fetureGet(emg, imu)
            # 数据缓存
            fetureCache.put([feture])
            # 识别
            t1 = threading.Thread(target=predict, args=(model, fetureCache.get(),))
            t1.start()
