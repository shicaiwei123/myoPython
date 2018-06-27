import threading

from tornado.websocket import WebSocketHandler
from tornado import gen

import tornado.web
import tornado.ioloop
import logging


user_set = dict()
data = list()
lock = threading.Lock()


@gen.coroutine
def second_loop():
    while True:
        ShowWebSocket.find_data()
        yield gen.sleep(1)


class ShowWebSocket(WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    @classmethod
    def put_data(cls, msg_type, msg):
        lock.acquire()
        data.append({"type": msg_type, "msg": msg})
        print("put_data success")
        lock.release()

    @classmethod
    def find_data(cls):
        lock.acquire()
        if len(data) != 0:
            msg_info = data[0]
            del data[0]
            cls.push_data(msg_info["type"], msg_info["msg"])
        lock.release()
        print("find_data_success")

    def check_origin(self, origin):
        return True

    def open(self):
        try:
            username = self.get_query_argument("username")
        except tornado.web.MissingArgumentError:
            username = "default"

        user_set[username] = self
        print("WebSocket opened")
        self.write_message("0+连接成功")

    def on_message(self, message):
        self.write_message(u"0+" + message)

    def on_close(self):
        print("Websocket closed")

    @classmethod
    def push_data(cls, type, msg):
        for key, user in user_set.items():
            try:
                user.write_message(type + "+" + msg)
            except tornado.websocket.WebSocketClosedError:
                logging.error("Error sending message", exc_info=True)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", ShowWebSocket)
        ]
        super(Application, self).__init__(handlers)


def start():
    tornado.ioloop.IOLoop.current().start()


def main():
    app = Application()
    app.listen("2233")
    tornado.ioloop.IOLoop.current().spawn_callback(second_loop)
    threading.Thread(target=start).start()


if __name__ == "__main__":
    main()