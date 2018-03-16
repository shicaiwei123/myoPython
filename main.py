# coding=utf-8
from getData.getData import *
from myoAnalysis import *





#译码，将识别到的标签翻译成手势含义
# def decode(label):
#     dict=\
#         {#称呼
#          1:'大家',2:'你',3:'我',4:'他',5:'和',6:'同学',7:'朋友',8:'儿子',9:'女儿',10:'爸爸'\
#          11:'妈妈',12:'爷爷',13:'奶奶',14:'人'\
#          #时间
#          31:'',32:'',33:'',34:,'',\
#     }
#     #



# isSave取True时时存储数据，取False时时分析数据
if __name__ == '__main__':

    m = init()
    # whether to save data
    isSave = False

    # 导入模型

    # 如果是存储数据
    if isSave:
        emgData = []
        imuData = []
        threshold = []
        try:
            while True:
                emg, imu = getOnceData(m)
                emgData.append(emg)
                imuData.append(imu)
                E = engery(emg)
                threshold.append([E])
                if HAVE_PYGAME:
                    for ev in pygame.event.get():
                        if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
                            testXlwt('emgData.xls', emgData)
                            testXlwt('imuData.xls', imuData)
                            testXlwt('threshold.xls', threshold)
                            raise KeyboardInterrupt()
                        elif ev.type == KEYDOWN:
                            if K_1 <= ev.key <= K_3:
                                m.vibrate(ev.key - K_0)
                            if K_KP1 <= ev.key <= K_KP3:
                                m.vibrate(ev.key - K_KP0)
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
        # 预测函数，用于多线程的回调
        #isFinsh 是线程锁
        isFinish=False
        def predict(model, data):
            t1=time.time()
            global isFinish
            result = model.predict(data)
            t2=time.time()
            isFinish=True
            print(t2-t1)    #测试识别时间
            print(result)   #输出结果
            # return result


        threads = []
        model=joblib.load('KNN')
        emg=[]
        imu=[]
        fetureCache=queue.Queue(10)
        while True:
             emg,imu = getGestureData(m)
             if emg==10000:
                 break
             np.save('emg',emg)
             np.save('imu',imu)
             feture=fetureGet(emg,imu)
             fetureCache.put([feture])
             t1 = threading.Thread(target=predict, args=(model,fetureCache.get(),))
             # r=model.predict([feture])
             t1.start()
             # print(r)
