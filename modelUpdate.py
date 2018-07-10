'''如果用户测试觉得新数据的效果可以，则可以将集成的新数据放到原始数据之中重新训练'''
'''更新原始数据缓存，并且将采集的数据的xls删除'''


from myoAnalysis import getNpyData
from myoAnalysis import getSVM
from sklearn.externals import joblib
from myoAnalysis import saveNpyDataOne
from myoAnalysis import saveNpyDataTwo
import os
import shutil

'''单手数据'''
oldOneFeaturePath = 'GetDataSet/oneFeature.npy'
oldOneLabelPath = 'GetDataSet/oneLabel.npy'
newOneFeaturePath = 'GetDataSet/oneFeatureCache.npy'
newOneLabelPath = 'GetDataSet/oneLabelCache.npy'
'''如果有新数据，则更新'''
if os.path.exists(newOneFeaturePath):
    oldOneFeature, oldOneLabel = getNpyData(oldOneFeaturePath, oldOneLabelPath)
    newOneFeature, newOneLabel = getNpyData(newOneFeaturePath, newOneLabelPath)
    oneFeature = oldOneFeature + newOneFeature
    oneLabel = oldOneLabel + newOneLabel
    modelOne = getSVM(oneFeature, oneLabel)
    joblib.dump(modelOne, 'SVM3One')
    if os.path.exists('GuestData/one'):
        shutil.rmtree('GuestData/one')
    os.remove(newOneFeaturePath)
    os.remove(newOneLabelPath)
    os.chdir('GetDataSet/')
    saveNpyDataOne(oneFeature, oneLabel, flag=1)
    lastPath=os.path.pardir
    os.chdir(lastPath)

'''双手数据'''
oldTwoFeaturePath = 'GetDataSet/twoFeature.npy'
oldTwoLabelPath = 'GetDataSet/twoLabel.npy'
newTwoFeaturePath = 'GetDataSet/twoFeatureCache.npy'
newTwoLabelPath = 'GetDataSet/twoLabelCache.npy'
'''如果有新数据，则更新'''
if os.path.exists(newTwoFeaturePath):
    oldTwoFeature, oldTwoLabel = getNpyData(oldTwoFeaturePath, oldTwoLabelPath)
    newTwoFeature, newTwoLabel = getNpyData(newTwoFeaturePath, newTwoLabelPath)
    twoFeature = oldTwoFeature + newTwoFeature
    twoLabel = oldTwoLabel + newTwoLabel
    if os.path.exists('GuestData/two'):
        shutil.rmtree('GuestData/two')
    os.remove(newTwoFeaturePath)
    os.remove(newTwoLabelPath)
    modelTwo = getSVM(twoFeature, twoLabel)
    joblib.dump(modelTwo, 'SVM3Two')
    os.chdir('GetDataSet/')
    saveNpyDataTwo(twoFeature, twoLabel, flag=1)
print('模型更新完成')
