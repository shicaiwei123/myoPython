#veriso = ""
#description =""
#author = "shicaiwei"
# -*- coding: <encoding name> -*-

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

# import matplotlib.pyplot as plt
#
# x = [1,2,3,4,5,6,7,8]
# y = [5,2,4,2,1,4,5,2]
#
# plt.scatter(x,y, label='skitscat', color='k', s=25, marker="o")
#
# plt.xlabel('x')
# plt.ylabel('y')
# plt.title('Interesting Graph\nCheck it out')
# plt.legend()
# plt.show()



# 读取mat数据测试
import scipy.io as scio
# data=scio.loadmat('/home/intel/data/1.mat')
# w=data['data']
# emgData=w['emgData']
# imuData = w['imuData']
# labels = w['lables']
# emgData=emgData[0,0]
# imuData=imuData[0,0]
# labels=labels[0,0]
# nonZeroLable=np.nonzero(emgData[:,0])
# row=np.size(nonZeroLable)
# emgData=emgData[0:row,:] #此时数据就可以直接使用了。0也去掉了
# imuData=imuData[0:row,:]
# print(labels)
# print(nonZeroLable)
# print(emgData)
# # print(a)
# print(data.keys())


# #测试新数据结构
# emg=np.load('emg.npy')
# imu=np.load('imu.npy')
# emg1=emg[:,1]
# a=np.shape(emg1)
# b=np.shape(imu)
# print(emg1)
# print(b)


#数字字符串转测试
# a=1
# b=str(a)
# print(b)
# c=b+'.mat'
# print(c)


#测试双线程
# import threading
# from time import ctime,sleep
#
#
# def music(a):
#     for i in range(2):
#         b=a*2
#         print ("I was listening to %d" %(b))
#         sleep(1)
#
# def move(a):
#     for i in range(2):
#         b=a**2
#         print ("I was listening to %d" %(b))
#         sleep(5)
#
#
#
# if __name__ == '__main__':
#     a=4
#     threads = []
#     t1 = threading.Thread(target=music, args=(a,))
#     threads.append(t1)
#     t2 = threading.Thread(target=move, args=(a,))
#     threads.append(t2)
#     while True:
#         for t in threads:
#             t.setDaemon(True)
#             t.start()
#
#     print("all over %s" %ctime())


# #python队列测试
# import queue
# q=queue.Queue(10)
# for i in range(20):
#     q.put(i)
#     if i>8:
#         print(q.get())
# while not q.empty():
#     print(q.get())


#字典测试
# dict=\
#     {1:'大家'\
#     ,2:'你'}
# print(dict[1])
#
# 分割测试
# from getData.getData import  *
# m=init()
# active = 1
# quiet = 1
# dataTimes = 1
# emgData = []
# imuData = []
# emg = []  # 缓存5次
# gyo=[]
# isactive=False
# isDown=False
# gyoLatter=0
# gyoFormer=0
# segTimes = 0;
# while True:
#     if HAVE_PYGAME:
#         for ev in pygame.event.get():
#             if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
#
#                 m.disconnect()
#                 break
#     emgCache, imuCache, emgRaw = getOnceData(m)
#     # print(emgCache )
#     # print(imuCache)
#     emgData.append(emgCache)
#     imuData.append(imuCache)
#     emg = emg + emgCache
#     gyo = gyo+imuCache[4:6]
#
#     # 分割
#     if dataTimes < 5:
#         dataTimes = dataTimes + 1
#
#     else:
#         gyoE = gyoEngery(gyo)
#         gyoFormer=gyoLatter
#         gyoLatter=gyoE
#         # print(gyoE)
#         emgData=[]
#         imuData=[]
#         gyo=[]
#         dataTimes=1
#         if gyoE>50:
#             isactive=True
#         if isactive:
#             gyoSub=gyoFormer-gyoLatter
#             if gyoSub<0:
#                 if gyoLatter<200:
#                     isactive=False
#                     print(segTimes)
#                     segTimes+=1

#matplotlib绘图

# import numpy as np
# from matplotlib import pyplot as plt
# from matplotlib import animation
#
# # first set up the figure, the axis, and the plot element we want to animate
# fig = plt.figure()
# ax1 = fig.add_subplot(2, 1, 1, xlim=(0, 2), ylim=(-4, 4))
# ax2 = fig.add_subplot(2, 1, 2, xlim=(0, 2), ylim=(-4, 4))
# line, = ax1.plot([], [], lw=2)
# line2, = ax2.plot([], [], lw=2)
#
#
# def init():
#     line.set_data([], [])
#     line2.set_data([], [])
#     return line, line2
#
#
# # animation function.  this is called sequentially
# def animate(i):
#     x = np.linspace(0, 2, 100)
#     y = np.sin(2 * np.pi * (x - 0.01 * i))
#     line.set_data(x, y)
#
#     x2 = np.linspace(0, 2, 100)
#     y2 = np.cos(2 * np.pi * (x2 - 0.01 * i)) * np.sin(2 * np.pi * (x - 0.01 * i))
#     line2.set_data(x2, y2)
#     return line, line2
#
#
# anim1 = animation.FuncAnimation(fig, animate, init_func=init, frames=50, interval=10)
# plt.show()



#
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib import animation
#
# # New figure with white background
# fig = plt.figure(figsize=(6,6), facecolor='white')
#
# # New axis over the whole figure, no frame and a 1:1 aspect ratio
# ax = fig.add_axes([0, 0, 1, 1], frameon=False, aspect=1)
#
# # Number of ring
# n = 50
# size_min = 50
# size_max = 50 ** 2
#
# # Ring position
# pos = np.random.uniform(0, 1, (n,2))
#
# # Ring colors
# color = np.ones((n,4)) * (0,0,0,1)
# # Alpha color channel geos from 0(transparent) to 1(opaque)
# color[:,3] = np.linspace(0, 1, n)
#
# # Ring sizes
# size = np.linspace(size_min, size_max, n)
#
# # Scatter plot
# scat = ax.scatter(pos[:,0], pos[:,1], s=size, lw=0.5, edgecolors=color, facecolors='None')
#
# # Ensure limits are [0,1] and remove ticks
# ax.set_xlim(0, 1), ax.set_xticks([])
# ax.set_ylim(0, 1), ax.set_yticks([])
#
# def update(frame):
#     global pos, color, size
#
#     # Every ring is made more transparnt
#     color[:, 3] = np.maximum(0, color[:,3]-1.0/n)
#
#     # Each ring is made larger
#     size += (size_max - size_min) / n
#
#     # Reset specific ring
#     i = frame % 50
#     pos[i] = np.random.uniform(0, 1, 2)
#     size[i] = size_min
#     color[i, 3] = 1
#
#     # Update scatter object
#     scat.set_edgecolors(color)
#     scat.set_sizes(size)
#     scat.set_offsets(pos)
#
#     # Return the modified object
#     return scat,
#
# anim = animation.FuncAnimation(fig, update, interval=10, blit=True, frames=200)
# plt.show()
#



# from matplotlib import pyplot as plt
# from matplotlib import animation
# import numpy as np
# import seaborn as sns
# sns.set_style("whitegrid")
#
#
# def randn_point():
#     # 产生随机散点图的x和y数据
#     x=np.random.randint(1,100,3)
#     y=np.random.randint(1,2,3)
#     return x,y
#
# # 创建画布，包含2个子图
# fig = plt.figure(figsize=(15, 10))
# ax1 = fig.add_subplot(2, 1, 1)
# ax2 = fig.add_subplot(2, 1, 2)
#
# # 先绘制初始图形，每个子图包含1个正弦波和三个点的散点图
# x = np.arange(0, 2*np.pi, 0.01)
#
# line1, = ax1.plot(x, np.sin(x)) # 正弦波
# x1,y1=randn_point()
# sca1 = ax1.scatter(x1,y1)   # 散点图
#
# line2, = ax2.plot(x, np.cos(x))  # 余弦波
# x2,y2=randn_point()
# sca2 = ax2.scatter(x2,y2)   # 散点图
#
# def init():
#     # 构造开始帧函数init
#     # 改变y轴数据，x轴不需要改
#     line1.set_ydata(np.sin(x))
#     line1.set_ydata(np.cos(x))
#     # 改变散点图数据
#     x1, y1 = randn_point()
#     x2, y2 = randn_point()
#     data1 = [[x,y] for x,y in zip(x1,y1)]
#     data2 = [[x, y] for x, y in zip(x2, y2)]
#     sca1.set_offsets(data1)  # 散点图
#     sca2.set_offsets(data2)  # 散点图
#     label = 'timestep {0}'.format(0)
#     ax1.set_xlabel(label)
#     return line1,line2,sca1,sca2,ax1  # 注意返回值，我们要更新的就是这些数据
#
# def animate(i):
#     # 接着，构造自定义动画函数animate，用来更新每一帧上各个x对应的y坐标值，参数表示第i帧
#     # plt.cla() 这个函数很有用，先记着它
#     line1.set_ydata(np.sin(x + i/10.0))
#     line2.set_ydata(np.cos(x + i / 10.0))
#     x1, y1 = randn_point()
#     x2, y2 = randn_point()
#     data1 = [[x,y] for x,y in zip(x1,y1)]
#     data2 = [[x, y] for x, y in zip(x2, y2)]
#     sca1.set_offsets(data1)  # 散点图
#     sca2.set_offsets(data2)  # 散点图
#     label = 'timestep {0}'.format(i)
#     ax1.set_xlabel(label)
#     return line1,line2,sca1,sca2,ax1
#
#
# # 接下来，我们调用FuncAnimation函数生成动画。参数说明：
# # fig 进行动画绘制的figure
# # func 自定义动画函数，即传入刚定义的函数animate
# # frames 动画长度，一次循环包含的帧数
# # init_func 自定义开始帧，即传入刚定义的函数init
# # interval 更新频率，以ms计
# # blit 选择更新所有点，还是仅更新产生变化的点。应选择True，但mac用户请选择False，否则无法显示动画
#
# ani = animation.FuncAnimation(fig=fig,
#                               func=animate,
#                               frames=100,
#                               init_func=init,
#                               interval=20,
#                               blit=True)
# plt.show()






import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
    graph_data = open('example.txt','r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    for line in lines:
        if len(line) > 1:
            x, y = line.split(',')
            xs.append(x)
            ys.append(y)
    ax1.clear()
    ax1.plot(xs, ys)


ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()







