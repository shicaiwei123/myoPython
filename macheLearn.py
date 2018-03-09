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
    w = data['w']
    emgData = w['emgData']
    imuData = w['imuData']
    labels = w['lables']
    emgData = emgData[0, 0]
    imuData = imuData[0, 0]
    labels = labels[0, 0]
    labels=labels[0,0]
    nonZeroLable = np.nonzero(emgData[:, 0])
    row = np.size(nonZeroLable)
    emgData = emgData[0:row, :]
    imuData = imuData[0:row, :]
    return emgData,imuData,labels


def getKNN(trainX,trainY):
    from  sklearn.neighbors import KNeighborsClassifier as knn
    model=knn(n_neighbors=10)
    model.fit(trainX,trainY)
    return model

if __name__ == '__main__':
    from sklearn.externals import joblib

    #读并且处理换粗特征值和标签，等待一起训练
    features=[]
    labels=[]
    #完成循环读取数据即可
    len=500   #数据总数
    for i in range(1,len):
        file ='data'+str(i)+'.mat'
        emg,imu,label=dataRead(file)
        feature=mAna.fetureGet(emg,imu)
        features.append(feature)
        labels.append(label)
    model=getKNN(feature,label)
    joblib.dump(model,'KNN')
    print(label)


