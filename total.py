import os
import threading
import multiprocessing

# def gesture():
#    # os.system("python ./SpeechRecognise.py")
#    os.system("python3 ./SpeechRecognise.py")
# t1 = threading.Thread(target=gesture)
# t1.start()

def server():
    os.system("python3 ./Server/server.py")

t2 = multiprocessing.Process(target=server)
t2.start()

os.system("python3 ./main.py")
#t1.join()
#t2.join()
