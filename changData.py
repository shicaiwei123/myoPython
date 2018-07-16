'''用于修改缓存的原始数据，去除一些不规范数据'''
'''比如 忙，高兴，怎么'''
import numpy as np
from myoAnalysis import getNpyData
from myoAnalysis import saveNpyDataTwo
from myoAnalysis import saveNpyDataOne


def getListIndex(listData, findData):
    '''
    用于获取指定数据的下标
    :param listData: 列表数据
    :param findData: 要查找的数据
    :return: 查找的数据的下标
    '''
    return [i for i, v in enumerate(listData) if v == findData]


'''删除单手数据'''
'''删除高兴，怎么'''
oneFeaturePath = 'GetDataSet/oneFeature.npy'
oneLabelPath = 'GetDataSet/oneLabel.npy'
# oneFeaturePath = 'oneFeature.npy'
# oneLabelPath = 'oneLabel.npy'
oneFeature, oneLabel = getNpyData(oneFeaturePath, oneLabelPath)
'''怎么，高兴'''
oneDeleteData = [[136], [233]]
for j in range(len(oneDeleteData)):
    oneFeatureIndex = getListIndex(oneLabel, oneDeleteData[j])
    for i in range(len(oneFeatureIndex)):
        del oneFeature[oneFeatureIndex[len(oneFeatureIndex) - i - 1]]
        del oneLabel[oneFeatureIndex[len(oneFeatureIndex) - i - 1]]

saveNpyDataOne(oneFeature, oneLabel, flag=1)
'''删除双手数据'''
twoFeaturePath = 'GetDataSet/twoFeature.npy'
twoLabelPath = 'GetDataSet/twoLabel.npy'
twoFeature, twoLabel = getNpyData(twoFeaturePath, twoLabelPath)
'''忙'''
twoDeleteData = [[228]]
for j in range(len(twoDeleteData)):
    twoFeatureIndex = getListIndex(twoLabel, twoDeleteData[j])
    for i in range(len(twoFeatureIndex)):
        del twoFeature[twoFeatureIndex[len(twoFeatureIndex) - i - 1]]
        del twoLabel[twoFeatureIndex[len(twoFeatureIndex) - i - 1]]

saveNpyDataTwo(twoFeature, twoLabel, flag=1)
