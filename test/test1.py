# veriso = ""
# description =""
# author = "shicaiwei"

# import matlab.engine
#
# eng=matlab.engine.start_matlab()
# a=eng.sqrt(4.0)
# print(a)
# eng.quit()
import numpy as np
# 测试图像----完成
# import  matplotlib.pyplot as plt
# import matplotlib.image as mimg
# a=[1,2,3,4,5]
# img=mimg.imread('1.jpg')
# plt.imshow(img)
# plt.plot(a)
# plt.show()


# 读取mat数据测试
import scipy.io as scio

data = scio.loadmat('/home/intel/data/1.mat')
w = data['w']
emgData = w['emgData']
imuData = w['imuData']
labels = w['lables']
emgData = emgData[0, 0]
imuData = imuData[0, 0]
labels = labels[0, 0]
nonZeroLable = np.nonzero(emgData[:, 0])
row = np.size(nonZeroLable)
emgData = emgData[0:row, :]  # 此时数据就可以直接使用了。0也去掉了
imuData = imuData[0:row, :]
print(labels)
print(nonZeroLable)
print(emgData)
# print(a)
print(data.keys())

# #测试新数据结构
# emg=np.load('emg.npy')
# imu=np.load('imu.npy')
# emg1=emg[:,1]
# a=np.shape(emg1)
# b=np.shape(imu)
# print(emg1)
# print(b)


# 数字字符串转测试
# a=1
# b=str(a)
# print(b)
# c=b+'.mat'
# print(c)
