'''用户模型回退，可以回退到过去的10个节点
   回退之后，当前的数据会被完全清空'''
from myoAnalysis import getFloderNumber
import os
import sys
import shutil
currentPath = os.getcwd()
versionCount = getFloderNumber('Backup')
versionBackPath = 'Backup/' + str(versionCount)

'''模型恢复'''
os.remove('SVM3One')
os.remove('SVM3Two')
shutil.move(versionBackPath + '/SVM3One', currentPath)
shutil.move(versionBackPath + '/SVM3Two', currentPath)

'''xls数据恢复'''
shutil.rmtree('GuestData')
shutil.move(versionBackPath + '/GuestData', currentPath)

'''GetDataSet恢复'''
shutil.rmtree('GetDataSet')
shutil.move(versionBackPath + '/GetDataSet', currentPath)

shutil.rmtree(versionBackPath)
print('回退完成')
