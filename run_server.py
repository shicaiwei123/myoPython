import os
import threading

def server():
    os.system("python3 ./Server/server.py")

t1 = threading.Thread(target=server)
t1.start()
t1.join()
