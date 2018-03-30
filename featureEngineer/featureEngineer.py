import numpy as np
import scipy.io as scio
import myoAnalysis as mAna


def dataRead(file):
    data=scio.loadmat(file)
    w = data['data']
    emgData = w['emgData']
    imuData = w['imuData']
    labels = w['lables']
    len=w['len']
    emgData = emgData[0, 0]
    imuData = imuData[0, 0]
    labels = labels[0, 0]
    len=len[0,0]
    row=(len-1)*5-1
    row=row[0,0]
    emgData = emgData[0:row, :]
    imuData = imuData[0:row, :]
    #归一化
    emgMax=np.max(np.max(emgData))
    imuMax=np.max(np.max(imuData))
    imuMin=np.min(np.min(imuData))
    emgData=(emgData)/emgMax
    imuData=(imuData-imuMin)/(imuMax-imuMin)
    return emgData,imuData,labels




features = []
labels = []
len = 1296  # 数据总数
#获取特征和标签

for i in range(1, len):
    file = '/home/intel/dataOneFiginer/' + str(i) + '.mat'
    emg, imu, label = dataRead(file)
    feature = mAna.fetureGet(emg, imu)
    features.append(feature)
    labels.append([label])



#特征工程

# from sklearn.feature_selection import SelectKBest
# from sklearn.feature_selection import chi2
#
# features=np.array(features)
# labels=np.array(labels)
#
# SelectKBest(chi2, k=20).fit_transform(features, labels)

from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier as knn
#递归特征消除法，返回特征选择后的数据
#参数estimator为基模型
#参数n_features_to_select为选择的特征个数
RFE(estimator=knn(), n_features_to_select=20).fit_transform(features, labels)

