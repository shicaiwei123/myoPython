
import numpy as np
from myoAnalysis import featureGetTwo, featureGet, matRead
from myoAnalysis import getKNN, getSVM
import os




def getModel(path=None):
    """
    获取训练模型
    :param path:  训练数据路径
    :return: 模型和识别准确率
    """
    dirData = os.listdir(path)
    length = len(dirData)  # 数据总数,
    #单纯训练模型
    # 训练
    # 读并且处理换粗特征值和标签，等待一起训练
    features = []
    labels = []
    counter = 1
    for i in range(1, length):  # 数据分割，一部分用于训练，一部分用于测试
        file = path + str(i) + '.mat'
        emgRight, imuRight, emgLeft, imuLeft, label, dataType = matRead(file)
        # 如果是单手
        if dataType == 1:
            feature = featureGet(emgRight, imuRight, divisor=8)
            features.append(feature)
            labels.append([label])
        else:
            feature = featureGetTwo(emgRight, imuRight, emgLeft, imuLeft, divisor=4)
            features.append(feature)
            labels.append([label])

    # 训练模型
    model = getSVM(features, labels)


    # 训练和测试
    #训练
    # 读并且处理换粗特征值和标签，等待一起训练
    features = []
    labels = []
    counter = 1
    for i in range(1, length):  # 数据分割，一部分用于训练，一部分用于测试
        if i % 10 == 0:
            counter = counter + 1
            if counter == 8:
                counter = 1
        if counter != 1:
            file = path + str(i) + '.mat'
            emgRight, imuRight, emgLeft, imuLeft, label, dataType = matRead(file)
            # 如果是单手
            if dataType == 1:
                feature = featureGet(emgRight, imuRight, divisor=8)
                features.append(feature)
                labels.append([label])
            else:
                feature = featureGetTwo(emgRight, imuRight, emgLeft, imuLeft, divisor=4)
                features.append(feature)
                labels.append([label])

    # 训练模型
    modelTest = getSVM(features, labels)
    # joblib.dump(model, modelName)
    feature = []
    labels = []
    result = []
    counter = 1
    right = 1
    wrong = 1
    a = []
    for i in range(1, length):
        if i % 10 == 0:  # 集满十次
            counter = counter + 1
            if counter == 8:
                counter = 1
        if counter == 1:
            file = path + str(i) + '.mat'
            emgRight, imuRight, emgLeft, imuLeft, label, dataType = matRead(file)
            if dataType == 1:
                feature = featureGet(emgRight, imuRight, divisor=8)
                labels.append([label])
            else:
                feature = featureGetTwo(emgRight, imuRight, emgLeft, imuLeft, divisor=4)
                labels.append([label])
            r = modelTest.predict([feature])
            result.append(r)
            # 结论
            if r == label:
                right = right + 1
            else:
                wrong = wrong + 1
    score = right / (right + wrong)
    return model,score


if __name__ == '__main__':

#初始化
    parentPath = os.path.abspath(os.path.dirname(os.getcwd()))
    path = parentPath + '/allDataOne6/'
    modelOne,accuracy=getModel(path)