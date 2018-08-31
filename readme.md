# 目标

- 基于Myo手环，获取手运动时的imu和emg数据，进行手语识别，将手语翻译成文字，
并且调用语音合成模块将文字转换成语音。

- 利用麦克风采集语音信息进行语音识别，将识别结果转成文字显示在上位机上给聋哑人看。

# 工程介绍

## 代码架构

- Myo手环底层驱动包 (Bean)

- Myo手环数据获取包 (GetData)
- 数据分析包 (DataAnalysis)
- 机器学习包 (MachineLearning)
- 语音识别包 (SpeechRecognise)
- 语音合成包 (SpeechSybthesis)
- 数据集获取和用户自校准包 (GetDataSet)

- 主模块 (主工程目录下的文件)


## 实现功能

- 运动检测和手势分割：获取一个手语手势的运动数据
- 语音识别：将语音转换成文字
- 语音合成：将文字转换成语音
- 机器学习：训练数据集，获得分类模型
- 用户自校正：用户可以根据自己使用体验，加入自己的数据重新训练模型，提高识别准确率
- 数据更新：用户如果觉得自己的自矫正后的效果很好，可以将采集的数据加入到原始数据中当做新的原始数据
完成一次数据的更新迭代
- 版本回退：用户如果发现自矫正效果反而变差，可以回退到上一个矫正版本

- 数据集扩充：用户可以自己扩充想要使用的手势


 



