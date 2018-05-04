import scipy.io as scio
import numpy as np
import sklearn
import myoAnalysis as mAna
# mat数据结构
# 包含结构体w
# w包含四个数据，emgData imuData len以及 lables
# len是包含了，但是当时统计错误
# nonZeoLabel是非0数组下标，row是非0数据行数
# 读取数据


def dataRead(file):
    from sklearn import preprocessing as pre
    data = scio.loadmat(file)
    w = data['data']
    dataType = w['dataType']
    dataType = dataType[0, 0]
    dataType = dataType[0, 0]
    if dataType == 2:
        emgRight = w['emgRight']
        imuRight = w['imuRight']
        emgRight = emgRight[0, 0]
        imuRight = imuRight[0, 0]
        emgLeft = w['emgLeft']
        imuLeft = w['imuLeft']
        emgLeft = emgLeft[0, 0]
        imuLeft = imuLeft[0, 0]
        labels = w['Lable']
        labels = labels[0, 0]
    else:
        emgRight = w['emgData']
        imuRight = w['imuData']
        emgRight = emgRight[0, 0]
        imuRight = imuRight[0, 0]
        labels = w['lables']
        labels = labels[0, 0]
    len = w['len']
    len = len[0, 0]
    row = len * 5
    row = row[0, 0]
    emgRight = emgRight[0:row, :]
    imuRight = imuRight[0:row, :]
    if dataType == 2:
        emgLeft = emgLeft[0:row, :]
        imuLeft = imuLeft[0:row, :]


    # 归一化
    emgMax = np.max(np.max(emgRight))
    imuMax = np.max(np.max(imuRight))
    imuMin = np.min(np.min(imuRight))
    emgRight = (emgRight) / emgMax
    imuRight = (imuRight - imuMin) / (imuMax - imuMin)
    if dataType == 2:
        emgMax = np.max(np.max(emgLeft))
        imuMax = np.max(np.max(imuLeft))
        imuMin = np.min(np.min(imuLeft))
        emgLeft = (emgLeft) / emgMax
        imuLeft = (imuLeft - imuMin) / (imuMax - imuMin)
    if dataType == 1:
        emgLeft = 0
        imuLeft = 0
    return emgRight, imuRight, emgLeft, imuLeft, labels, dataType


def getKNN(trainX, trainY):
    from sklearn.neighbors import KNeighborsClassifier as knn
    trainX = np.array(trainX)
    trainY = np.array(trainY)
    model = knn(n_neighbors=30, weights='distance')
    model.fit(trainX, trainY.ravel())
    return model


def getSVM(trainX, trainY):
    from sklearn.svm import SVC
    trainX = np.array(trainX)
    trainY = np.array(trainY)
    model = SVC(kernel='rbf', degree=3)
    model.fit(trainX, trainY.ravel())
    return model


if __name__ == '__main__':
    from sklearn.externals import joblib
    import os
    parentPath = os.path.abspath(os.path.dirname(os.getcwd()))
    path = parentPath + '/matDataTwo1/'
    # 训练和测试
    isLearn = True
    modelName = 'KNN30Two'
    dirData = os.listdir(path)
    len = len(dirData)  # 数据总数,

    if isLearn:
        # 读并且处理换粗特征值和标签，等待一起训练
        features = []
        labels = []
        counter = 1
        a = []
        for i in range(1, len):
            if i % 10 == 0:  # jimanshici
                counter = counter + 1
                if counter == 8:
                    counter = 1
            if counter != 1:
                a.append(i)
                file = path + str(i) + '.mat'
                emgRight, imuRight, emgLeft, imuLeft, label, dataType = dataRead(file)
                # 如果是单手
                if dataType == 1:
                    feature = mAna.featureGet(emgRight, imuRight,divisor=4)
                    features.append(feature)
                    labels.append([label])
                else:
                    feature = mAna.featureGetTwo(emgRight, imuRight, emgLeft, imuLeft)
                    features.append(feature)
                    labels.append([label])

        # 训练模型
        model = getKNN(features, labels)
        joblib.dump(model, modelName)
    else:
        feature = []
        labels = []
        result = []
        counter = 1
        right = 1
        wrong = 1
        model = joblib.load(modelName)
        a = []
        for i in range(1, len):
            if i % 10 == 0:  # 集满十次
                counter = counter + 1
                if counter == 8:
                    counter = 1
            if counter == 1:
                # a.append(i)
                file = path + str(i) + '.mat'
                emgRight, imuRight, emgLeft, imuLeft, label = dataRead(file)
                if emgLeft == 0:
                    feature = mAna.featureGet(emgRight, imuRight)
                    label.append([label])
                else:
                    feature = mAna.featureGetTwo(emgRight, imuRight, emgLeft, imuLeft)
                    label.append([label])
                r = model.predict([feature])
                result.append(r)
                # jielunjieguo
                if r == label:
                    right = right + 1
                else:
                    wrong = wrong + 1
        score = right / (right + wrong)
        # chucunjieguo
        labels = np.array(labels)
        result = np.array(result)
        # np.save('labels',labels)
        # np.save('result',result)
        print(score)
        # print(a)
