"""
程序入口函数
将手势识别功能和语音合成功能加载到系统的进程之中，以多线程的方式运行
"""

import os
import threading
import multiprocessing
import argparse

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--new", action="store_true")
    return parser.parse_args()


def gesture():
#   os.system("python  ./SpeechRecognise/SpeechRecognise.py")
    os.system("python3 ./SpeechRecognise/SpeechRecognise.py")

options = parse()
t1 = threading.Thread(target=gesture)
t1.setDaemon(True)
t1.start()

def myo():
    if options.new:
        os.system("python3 ./gestureRecognition.py --new")
    else:
        os.system("python3 ./gestureRecognition.py")
    
#def server():
#    os.system("python3 ./Server/server.py")

t2 = threading.Thread(target=myo)
t2.setDaemon(True)
t2.start()

t1.join()
