
import numpy as np
from myoAnalysis import getMatFeature
from myoAnalysis import getModel
import os



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
