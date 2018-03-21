import  scipy.io as scio
import  numpy as np
import sklearn
import myoAnalysis as mAna
#mat数据结构
#包含结构体w
#w包含四个数据，emgData imuData len以及 lables
#len是包含了，但是当时统计错误
#nonZeoLabel是非0数组下标，row是非0数据行数
#读取数据
def dataRead(file):
    data=scio.loadmat(file)
    w = data['data']
    emgData = w['emgData']
    imuData = w['imuData']
    labels = w['lables']
    len=w['len']
    emgData = emgData[0, 0]
    imuData = imuData[0, 0]
    labels = labels[0, 0]
    len=len[0,0]
    row=(len-1)*5-1
    row=row[0,0]
    emgData = emgData[0:row, :]
    imuData = imuData[0:row, :]
    #归一化
    emgMax=np.max(np.max(emgData))
    imuMax=np.max(np.max(imuData))
    imuMin=np.min(np.min(imuData))
    emgData=(emgData)/emgMax
    imuData=(imuData-imuMin)/(imuMax-imuMin)
    return emgData,imuData,labels


def getKNN(trainX,trainY):
    from  sklearn.neighbors import KNeighborsClassifier as knn
    trainX=np.array(trainX)
    trainY=np.array(trainY)
    model=knn(n_neighbors=10,metric='cosine',weights='distance')
    model.fit(trainX,trainY.ravel())
    return model


def getSVM(trainX,trainY):
    from  sklearn.svm import SVC
    trainX=np.array(trainX)
    trainY=np.array(trainY)
    model=SVC(kernel='rbf',degree=3)
    model.fit(trainX,trainY.ravel())
    return model


if __name__ == '__main__':
    from sklearn.externals import joblib
    #xunlieheceshi
    isLearn =False
    if isLearn:
        #读并且处理换粗特征值和标签，等待一起训练
        features=[]
        labels=[]
        counter=1
        len=1194  #数据总数
        a=[]
        for i in range(1,len):
            if i%10 ==0:     #jimanshici
                counter=counter+1
                if counter==8:
                    counter=1
            if counter!=1:
                a.append(i)
                file ='/home/intel/data/'+str(i)+'.mat'
                emg,imu,label=dataRead(file)
                feature=mAna.fetureGet(emg,imu)
                features.append(feature)
                labels.append([label])
        #训练模型
        model=getKNN(features,labels)
        joblib.dump(model,'KNN')
    else:
        feature = []
        labels = []
        result=[]
        counter = 1
        right=1
        wrong=1
        len = 1193  # 数据总数
        model=joblib.load('KNN')
        a = []
        for i in range(1, len):
            if i % 10 == 0:  # 集满十次
                counter = counter + 1
                if counter == 8:
                    counter = 1
            if counter == 1:
                # a.append(i)
                file ='/home/intel/data/'+str(i)+'.mat'
                emg,imu,label=dataRead(file)
                labels.append(label)
                feature=mAna.fetureGet(emg,imu)
                r=model.predict([feature])
                result.append(r)
                #jielunjieguo
                if r==label:
                    right=right+1
                else:
                    wrong=wrong+1
        score=right/(right+wrong)
        #chucunjieguo
        labels=np.array(labels)
        result=np.array(result)
        np.save('labels',labels)
        np.save('result',result)
        print(score)
        # print(a)



