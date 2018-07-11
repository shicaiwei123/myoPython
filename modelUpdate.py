'''如果用户测试觉得新数据的效果可以，则可以将集成的新数据放到原始数据之中重新训练'''
'''更新原始数据缓存，并且将采集的数据的xls以及更新前的数据数据全部放到备份区，方便回退'''


from myoAnalysis import getNpyData
from myoAnalysis import getSVM
from sklearn.externals import joblib
from myoAnalysis import saveNpyDataOne
from myoAnalysis import saveNpyDataTwo
from myoAnalysis import getFloderNumber
import os
import shutil

'''单手数据'''
oldOneFeaturePath = 'GetDataSet/oneFeature.npy'
oldOneLabelPath = 'GetDataSet/oneLabel.npy'
newOneFeaturePath = 'GetDataSet/oneFeatureCache.npy'
newOneLabelPath = 'GetDataSet/oneLabelCache.npy'
'''建立缓存文件夹'''
'''只缓存20个版本'''
if not os.path.exists('Backup'):
    os.makedirs('Backup')
backupCount = getFloderNumber('Backup/')
if backupCount < 20:
    backupCount = backupCount + 1
else:
    backupCount = 20
backupGetDataSet = 'Backup/' + str(backupCount) + '/GetDataSet'
backupGuestData = 'Backup/' + str(backupCount) + '/GuestData'
backup = 'Backup/' + str(backupCount)
'''会自动创建目标目录'''
shutil.copytree('GetDataSet', backupGetDataSet)
os.makedirs(backupGuestData)

'''如果有新数据，则更新'''
if os.path.exists(newOneFeaturePath):
    oldOneFeature, oldOneLabel = getNpyData(oldOneFeaturePath, oldOneLabelPath)
    newOneFeature, newOneLabel = getNpyData(newOneFeaturePath, newOneLabelPath)
    oneFeature = oldOneFeature + newOneFeature
    oneLabel = oldOneLabel + newOneLabel
    '''用户自定义数据的处理，不再是删除，而是也作为原始缓存'''
    os.remove(newOneFeaturePath)
    os.remove(newOneLabelPath)

    if os.path.exists('GuestData/one'):
        shutil.move('GuestData/one', backupGuestData)
    shutil.move('SVM3One', backup)

    modelOne = getSVM(oneFeature, oneLabel)

    joblib.dump(modelOne, 'SVM3One')
    os.chdir('GetDataSet/')
    saveNpyDataOne(oneFeature, oneLabel, flag=1)
    lastPath = os.path.pardir
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

    os.remove(newTwoFeaturePath)
    os.remove(newTwoLabelPath)

    if os.path.exists('GuestData/two'):
        shutil.move('GuestData/two', backupGuestData)
    shutil.move('SVM3Two', backup)

    modelTwo = getSVM(twoFeature, twoLabel)
    joblib.dump(modelTwo, 'SVM3Two')
    os.chdir('GetDataSet/')
    saveNpyDataTwo(twoFeature, twoLabel, flag=1)
    lastPath = os.path.pardir
    os.chdir(lastPath)
print('模型更新完成')
