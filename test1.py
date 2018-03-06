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

a=[1,2,3]
b=[4,5,6]
e=[]
# e.append(a)
# e.append(b)
e=e+a
e=e+b
c=np.array(e)
print(c.dtype)
print(c)
d=np.sum(c)
# c.reshape((1,6))
# c.append(a)
# c.append(b)
print(d)
print(c)
