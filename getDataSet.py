import getData.getData as myoData   #数据接口

def getDataSet(filename=None,handNumber=1,dataNumber=12):
    """


    :return: 没有返回值，
    """

class DataFormal():
    """
     :param filename:   文件夹名字，手势名字，比如'你好'，默认为空
    :param handNumber: 手势中手的需要用到的手的数目，单手为1双手为2，默认单手
    :param dataNumber: 要采集的的手势的个数，为了防止误差，第一个和最后一个采集的手势会被去掉，该值的设定是要采集的数据量加2，总共，默认是12
    """
    def __init__(self,fileName=None,handNumber=1,dataNumber=12):
        self.__fileName=fileName
        self.__handNumber=handNumber
        self.__dataNumber=dataNumber
if __name__ == '__main__':
    """
    获取数据
    """


