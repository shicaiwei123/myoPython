"""
调用讯飞接口将语音转换为文字
"""
import logging
from ctypes import cdll


class STT(object):

    def __init__(self):
        self.lib_path = "libmsc.so"
        self.logger = self.config_logger()
        self.lib = cdll.LoadLibrary(self.lib_path)   # 读取讯飞的SDK库


    @staticmethod
    def config_logger():
        logger = logging.getLogger("STT")
        formatter = logging.Formatter("%(asctime)s-%(name)s-%(message)s")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        logger.setLevel(logging.INFO)
        return logger

    def login(self, login_param="appid = 5af91976, work_dir = ."):
        """
        登录讯飞
        :param login_param: 登录参数
        :return:
        """
        login_ret = self.lib.MSPLogin(None, None, login_param)
        if login_ret != 0: # 登录失败
            raise ValueError("Login Failed")
        self.logger.info("Login succeed")

    def iat(self):