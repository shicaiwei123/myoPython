import os
import threading
def gesture():
    # os.system("python ./SpeechRecognise.py")
    os.system("python ./SpeechRecognise.py")
t1 = threading.Thread(target=gesture)
t1.start()

os.system("python ./test.py")