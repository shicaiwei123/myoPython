from DataAnalysis.myoAnalysis import getModel
import os
from sklearn.externals import joblib
from DataAnalysis.myoAnalysis import getNpyData

if __name__ == '__main__':
    '''用于数据更新之后，用户模型的训练'''
    '''输入是全部新的数据，输出是新的模型'''
    # 初始化
    '''如果置为真则训练'''
    isOne=True
    isTwo=True
    featuresOne = []
    labelsOne = []
    featuresTwo = []
    labelsTwo = []
    parentPath = os.path.dirname(os.getcwd())
    lastPath = os.path.pardir
    '''单手数据训练'''
    if isOne:
        initOneFeatureOldPath = lastPath + '/GetDataSet' + '/oneFeature.npy'
        initOneLabelOldPath = lastPath + '/GetDataSet'  + '/oneLabel.npy'
        initOneFeatureOld, initOneLabelOld = getNpyData(initOneFeatureOldPath, initOneLabelOldPath)
        '''新旧的都要读出来'''
        initOneFeature = initOneFeatureOld
        initOneLabel = initOneLabelOld
        modelOne, accuracy = getModel(initOneFeature,initOneLabel,0.2)
        joblib.dump(modelOne, 'SVM3One')
        print(accuracy)

    '''双手数据训练'''
    if isTwo:
        initTwoFeatureOldPath = lastPath+ '/GetDataSet' + '/twoFeature.npy'
        initTwoLabelOldPath = lastPath+ '/GetDataSet'  + '/twoLabel.npy'
        initTwoFeatureOld, initTwoLabelOld = getNpyData(initTwoFeatureOldPath, initTwoLabelOldPath)
        '''新旧的都要读出来'''
        initTwoFeature = initTwoFeatureOld
        initTwoLabel = initTwoLabelOld
        # 训练模型
        modelTwo, accuracy = getModel(initTwoFeature,initTwoLabel,0.2)
        joblib.dump(modelTwo, 'SVM3Two')
        print(accuracy)
