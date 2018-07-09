import threading

from tornado.websocket import WebSocketHandler
from tornado import gen
from functools import partial
import tornado.web
import tornado.ioloop
import logging
#import tornadoredis
import redis
import json

data = list()
lock = threading.Lock()
user_set = dict()

def redis_listener():
    r = redis.Redis(host="127.0.0.1")
    ps=r.pubsub()
    ps.subscribe(["voice", "gesture"])
    t_io_loop = tornado.ioloop.IOLoop.instance()
    for message in ps.listen():
        #print("get message", message)
        for key, user in user_set.items():
            t_io_loop.add_callback(user.write_message,str(message['data'], encoding="utf-8"))

@gen.coroutine
def second_loop():
    while True:
        ShowWebSocket.find_data()
        yield gen.sleep(1)


class ShowWebSocket(WebSocketHandler):

    user_set = dict()
    data = list()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.listen()

    @classmethod
    def put_data(cls, msg_type, msg):
        lock.acquire()
        cls.data.append({"type": msg_type, "msg": msg})
        print("put_data success")
        print(cls.data)
        lock.release()
    
    def connect(self):
        self.redis_client = tornadoredis.Client(host="127.0.0.1", port=6379)
        self.redis_client.connect()

    @tornado.gen.engine
    def listen(self):
        self.redis_client = tornadoredis.Client()
        self.redis_client.connect()
        yield tornado.gen.Task(self.redis_client.subscribe, "voice")
        self.redis_client.listen(self.on_update)
    
    @gen.coroutine
    def on_update(self, message):
        for key, user in user_set.items():
            user.write_message(message["type"] + "+" + message["data"])

    @classmethod
    def find_data(cls):
        lock.acquire()
        print("find_data: ", cls.data)
        if len(cls.data) != 0:
            msg_info = cls.data[0]
            print("find data success", msg_info)
            del cls.data[0]
            cls.push_data(msg_info["type"], msg_info["msg"])
        lock.release()
        # print("find_data_success")

    def check_origin(self, origin):
        return True

    def open(self):
        try:
            username = self.get_query_argument("username")
        except tornado.web.MissingArgumentError:
            username = "default"

        user_set[username] = self
        print("WebSocket opened")
        print(user_set)
        self.write_message(json.dumps({"type": "voice", "data": "Connect"}))

    def on_message(self, message):
        self.write_message(u"0+" + message)

    def on_close(self):
        print("Websocket closed")

    @classmethod
    def push_data(cls, type, msg):
        print("push data")
        print(cls.user_set)
        for key, user in cls.user_set.items():
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
    threading.Thread(target=redis_listener).start()
    app = Application()
    app.listen("2233", address='0.0.0.0')
    #tornado.ioloop.IOLoop.current().spawn_callback(redis_listener)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
