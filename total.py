import os
import threading
import multiprocessing
import argparse

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--new", action="store_true")
    return parser.parse_args()


def gesture():
#   os.system("python ./SpeechRecognise.py")
    os.system("python3 ./SpeechRecognise.py")

options = parse()
t1 = threading.Thread(target=gesture)
t1.setDaemon(True)
t1.start()

def myo():
    if options.new:
        os.system("python3 ./main.py --new")
    else:
        os.system("python3 ./main.py")
    
#def server():
#    os.system("python3 ./Server/server.py")

t2 = threading.Thread(target=myo)
t2.setDaemon(True)
t2.start()

t1.join()
#t2.join()
