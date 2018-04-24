from getData.getData import *
from myoAnalysis import *
from voice.speech import xf_speech

# speaker = xf_speech()    # 在minnowboard板子上无需设置端口号，默认'/dev/ttyS4'
# speaker = xf_speech('/dev/ttyUSB0')


# 译码，将识别到的标签翻译成手势含义
# def decode(label):
#
#     label=int(label)
#     dict=\
#         {#称呼
#          1:'大家',2:'你',3:'我',4:'他',5:'和',6:'同',7:'学',8:'男',9:'女',10:'爸爸',
#          11:'妈妈',12:'爷爷',13:'奶奶',14:'人',
#          #时间
#          31:'早上',32:'中午',33:'晚上',34:'年',
#          #礼貌用语
#          51:'请',52:'好',53:'谢谢',54:'谢谢',55:'不',56:'用',57:'早上',
#          #地点
#          71:'去',72:'在',73:'到',74:'家',75:'火车站',76:'机场',77:'汽车站',
#          #交通
#          101:'坐',102:'火车',103:'飞机',104:'公交车',105:'大巴',106:'地铁',
#          #证件
#          121:'证',122:'身份',123:'学生',
#          #疑问
#          131:'问',132:'什么',133:'多少',134:'哪里',
#          #数字
#          141:0,142:1,143:2,144:3,145:4,146:5,147:6,148:7,149:8,150:9,
#          151:10,152:20,153:30,154:40,155:50,156:60,157:70,158:80,159:90,
#          160:100,161:200,162:300,163:400,164:500,165:600,166:700,167:800,168:900,
#          #就餐
#          191:'吃',192:'饭',193:'饮料',194:'啤酒',195:'果汁',196:'钱',
#          #生活
#          211:'手机',212:'钱包',213:'没有',214:'看见',
#          #情绪
#          231:'爱',232:'对不起',233:'高兴',234:'危险',235:'误会',236:'想',237:'不要'
#     }
#     return dict[label]


# isSave取True时时存储数据，取False时时分析数据
if __name__ == '__main__':

    m = init()
    # shifoubaocunshuju
    isSave = False
    # 导入模型

    # 如果是存储数据
    if isSave:
        emgData = []  # 一次手势数据
        imuData = []  # 一次手势数据
        emgDataAll = []  # 所有数据
        imuDataAll = []
        engeryDataAll = []  # 所有数据
        engeryDataSeg = []  # 一次手势数据
        emgRawRightAll = []
        gestureCounter = 0
        try:
            while True:
                # emg, imu, emg_raw = getOnceData(m)
                emg, imu, emgAll, imuAll, engeryAll, engerySeg, emgRawAll = getGestureData(m)
                gestureCounter = gestureCounter + 1
                print(gestureCounter)
                if HAVE_PYGAME:
                    if emg == 10000:
                        name = '你是哪里人'
                        engeryDataSeg = engeryDataSeg + [[gestureCounter-1]]
                        saveExcle('wscData/oneFinger/' + name + '/emgData.xls', emgData)
                        saveExcle('wscData/oneFinger/' + name + '/imuData.xls', imuData)
                        saveExcle('wscData/oneFinger/' + name + '/emgDataAll.xls', emgDataAll)
                        saveExcle('wscData/oneFinger/' + name + '/imuDataAll.xls', imuDataAll)
                        saveExcle('wscData/oneFinger/' + name + '/engeryDataAll.xls', engeryDataAll)
                        saveExcle('wscData/oneFinger/' + name + '/engeryDataSeg.xls', engeryDataSeg)
                        saveExcle('wscData/oneFinger/' + name + '/emgRawRightAll.xls', emgRawRightAll)
                        # saveExcle('wscData/oneFinger/'+name+'/thresholdData.xls', threshold)
                        raise KeyboardInterrupt()
                emgData = emgData + emg + [[0]]
                # print(emg)
                imuData = imuData + imu + [[0]]

                emgDataAll = emgDataAll + emgAll
                imuDataAll = imuDataAll + imuAll
                engeryDataAll = engeryDataAll + engeryAll
                engeryDataSeg = engeryDataSeg + engerySeg + [[0]]
                emgRawRightAll = emgRawRightAll + emgRawAll

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
        model = joblib.load('KNN30')
        emg = []
        imu = []
        fetureCache = queue.Queue(10)
        while True:
            emg, imu,a,b,c,d,e = getGestureData(m)
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
