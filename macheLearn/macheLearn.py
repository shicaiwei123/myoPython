
import numpy as np
from  myoAnalysis import featureGetTwo,featureGet,dataRead


def getKNN(trainX, trainY):
    from sklearn.neighbors import KNeighborsClassifier as knn
    trainX = np.array(trainX)
    trainY = np.array(trainY)
    model = knn(n_neighbors=1, weights='distance')
    model.fit(trainX, trainY.ravel())
    return model


def getSVM(trainX, trainY):
    from sklearn.svm import SVC
    trainX = np.array(trainX)
    trainY = np.array(trainY)
    model = SVC(kernel='linear',degree=3)
    model.fit(trainX, trainY.ravel())
    return model


if __name__ == '__main__':
    global dddddd
    from sklearn.externals import joblib
    import os
    parentPath = os.path.abspath(os.path.dirname(os.getcwd()))
    path = parentPath + '/allDataOne6/'
    # 训练和测试
    isLearn = True
    modelName = 'SVM3One'
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
                # if i==574:
                #     print(i)
                file = path + str(i) + '.mat'
                emgRight, imuRight, emgLeft, imuLeft, label, dataType = dataRead(file)
                # 如果是单手
                if dataType == 1:
                    feature = featureGet(emgRight, imuRight, divisor=8)
                    features.append(feature)
                    labels.append([label])
                else:
                    # dddddd=dddddd+1
                    # print(dddddd)
                    feature = featureGetTwo(emgRight, imuRight, emgLeft, imuLeft,divisor=4)
                    features.append(feature)
                    labels.append([label])

        # 训练模型
        model = getSVM(features, labels)
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
                emgRight, imuRight, emgLeft, imuLeft, label, dataType = dataRead(file)
                if dataType == 1:
                    feature = featureGet(emgRight, imuRight,divisor=8)
                    labels.append([label])
                else:
                    feature = featureGetTwo(emgRight, imuRight, emgLeft, imuLeft,divisor=4)
                    labels.append([label])
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
