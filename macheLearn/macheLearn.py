
import numpy as np
from myoAnalysis import getMatFeature
from myoAnalysis import getModel
import os
from sklearn.externals import joblib


if __name__ == '__main__':
    '''用于数据更新之后，用户模型的训练'''
    '''输入是全部新的数据，输出是新的模型'''
    # 初始化
    '''如果置为真则训练'''
    isOne=True
    isTwo=False
    featuresOne = []
    labelsOne = []
    featuresTwo = []
    labelsTwo = []
    parentPath = os.path.dirname(os.getcwd())
    '''单手数据训练'''
    if isOne:
        pathOne = parentPath + '/Data/allDataOne10/'
        dirDataOne = os.listdir(pathOne)
        length = len(dirDataOne)  # 数据总数,
        for i in range(1, length):  # 数据分割，一部分用于训练，一部分用于测试
            fileOne = pathOne + str(i) + '.mat'
            featureOne, labelOne = getMatFeature(fileOne)
            labelOne = list(labelOne[0])
            featuresOne.append(featureOne)
            labelsOne.append(labelOne)
        modelOne, accuracy = getModel(featuresOne,labelsOne,0.2)
        joblib.dump(modelOne, 'SVM3One')
        print(accuracy)

    '''双手数据训练'''
    if isTwo:
        pathTwo = parentPath + '/Data/allDataTwo7/'
        dirDataTwo = os.listdir(pathTwo)
        length = len(dirDataTwo)  # 数据总数,
        for i in range(1, length):  # 数据分割，一部分用于训练，一部分用于测试
            fileTwo = pathTwo + str(i) + '.mat'
            featureTwo, labelTwo = getMatFeature(fileTwo)
            if len(featureTwo)==312:
                print(i)
            labelTwo = list(labelTwo[0])
            featuresTwo.append(featureTwo)
            labelsTwo.append(labelTwo)
        # 训练模型
        modelTwo, accuracy = getModel(featuresTwo,labelsTwo,0.2)
        joblib.dump(modelTwo, 'SVM3Two')
        print(accuracy)
