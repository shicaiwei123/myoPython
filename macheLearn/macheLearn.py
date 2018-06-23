
import numpy as np
from myoAnalysis import featureGetTwo, featureGet, getMatFeature
from myoAnalysis import getKNN, getSVM
import os
import random


def segData(feature, label, radio):
    """

    :param feature: 数据特征
    :param label: 数据标签，维度要和特征一直
    :param radio: 用于测试的数据比例
    :return: 训练数据，训练标签，
    """


def getModel(feature, label, ratio):
    """

    :param feature: 数据特征
    :param label: 数据标签，维度要和特征一直
    :param ratio: 用于测试的数据比例
    :return: 训练模型和准确度
    """

    " ""初始化 """
    length = len(feature)
    """模型训练"""
    model = getSVM(feature, label)
    """测试模型准确度"""
    """获取测试数据，训练数据"""
    learnLabel = []
    learnIndex = []
    number = length * (1 - ratio)
    learnData = random.sample(feature, number)
    for i in learnData:
        learnIndex.append(feature.index(i))
    learnIndex = tuple(learnIndex)
    allIndex = tuple(range(len(feature)))
    testIndex = set(allIndex).difference(set(learnIndex))
    for i in learnIndex:
        learnLabel.append(label[i])

    learnModel = getSVM(learnData, learnLabel)

    right = 0
    for i in testIndex:
        testData = feature[i]
        testLabel = label[i]
        testResult = learnModel.predict(testData)
        if testResult == testLabel:
            right = right + 1
    accuracy = right / len(testIndex)
    return model, accuracy


def getdataModel(path=None):
    """
    获取训练模型
    :param path:  训练数据路径
    :return: 模型和识别准确率
    """
    dirData = os.listdir(path)
    length = len(dirData)  # 数据总数,
    # 单纯训练模型
    # 训练
    # 读并且处理换粗特征值和标签，等待一起训练
    features = []
    labels = []
    counter = 1
    for i in range(1, length):  # 数据分割，一部分用于训练，一部分用于测试
        file = path + str(i) + '.mat'
        feature, label = getMatFeature(file)
        label = list(label[0])
        features.append(feature)
        labels.append(label)
    # 训练模型

    model = getSVM(features, labels)

    # 训练和测试
    # 训练
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
            feature, label = getMatFeature(file)
            label = list(label[0])
            features.append(feature)
            labels.append(label)
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
            feature, label = getMatFeature(file)
            label = label[0]
            r = modelTest.predict([feature])
            result.append(r)
            # 结论
            if r == label:
                right = right + 1
            else:
                wrong = wrong + 1
    score = right / (right + wrong)
    return model, score


if __name__ == '__main__':

    # 初始化
    features = []
    labels = []
    parentPath = os.path.dirname(os.getcwd())
    path = parentPath + '/allDataOne6/'
    dirData = os.listdir(path)
    length = len(dirData)  # 数据总数,
    for i in range(1, length):  # 数据分割，一部分用于训练，一部分用于测试
        file = path + str(i) + '.mat'
        feature, label = getMatFeature(file)
        label = list(label[0])
        features.append(feature)
        labels.append(label)
    # 训练模型
    modelOne, accuracy = getModel(features,labels,0.2)
    print(accuracy)
