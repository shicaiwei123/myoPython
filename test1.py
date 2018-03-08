#veriso = ""
#description =""
#author = "shicaiwei"

# import matlab.engine
#
# eng=matlab.engine.start_matlab()
# a=eng.sqrt(4.0)
# print(a)
# eng.quit()
import numpy as np
#测试图像----完成
# import  matplotlib.pyplot as plt
# import matplotlib.image as mimg
# a=[1,2,3,4,5]
# img=mimg.imread('1.jpg')
# plt.imshow(img)
# plt.plot(a)
# plt.show()


#读取mat数据测试
import  scipy.io as scio
data=scio.loadmat('1.mat')
w=data['w']
emgData=w['emgData']
emgData=emgData[0,0]

print(emgData)
# print(a)
print(data.keys())
