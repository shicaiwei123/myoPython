from getData.getData import *
from myoAnalysis import *


#译码，将识别到的标签翻译成手势含义
# def decode(label):

#isSave取True时时存储数据，取False时时分析数据
if __name__ == '__main__':


    m = init()
    #shifoubaocunshuju
    isSave = False
    #导入模型

    #如果是存储数据
    if isSave:
        emgData=[]
        imuData=[]
        threshold=[]
        try:
            while True:
                emg, imu = getOnceData(m)
                emgData.append(emg)
                imuData.append(imu)
                E=engery(emg)
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
    #否则是分析数据
    else:
        from sklearn.externals import joblib
        model=joblib.load('KNN')
        emg=[]
        imu=[]
        while True:
             emg,imu = getGestureData(m)
             if emg==10000:
                 break
             np.save('emg',emg)
             np.save('imu',imu)
             feture=fetureGet(emg,imu)
             r=model.predict([feture])
             print(r)
