#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from socketIO_client import SocketIO, LoggingNamespace
from dto.record import StreamDTO, ConfigDTO
from threading import Thread, RLock, Condition
import queue
import base64
import time
import copy
from socketIO_client import SocketIO, BaseNamespace

start_broadcasting = 0

class Namespace(BaseNamespace):

    def message(self, data):
        try:
            print("type", type(data))
            if isinstance(data, dict):
                if "operation" in data and data["operation"] == 'broadcasting':
                    global start_broadcasting
                    start_broadcasting = int(data["message"])
                print("message", data)
        except Exception as e:
            pass

    def on_message(self, data):
        try:
            print("type", type(data))
            if isinstance(data, dict):
                if "operation" in data and data["operation"] == 'broadcasting':
                    global start_broadcasting
                    start_broadcasting = int(data["message"])
                print("on_message", data)
        except Exception as e:
            pass
    
    def on_handle_message(self, data):
        try:
            print("type", type(data))
            if isinstance(data, dict):
                if "operation" in data and data["operation"] == 'broadcasting':
                    global start_broadcasting
                    start_broadcasting = int(data["message"])
            print("on_handle_message", data)
        except Exception as e:
            pass

    def handle_message(self, data):
        try:
            print("type", type(data))
            if isinstance(data, dict):
                if "operation" in data and data["operation"] == 'broadcasting':
                    global start_broadcasting
                    start_broadcasting = int(data["message"])
            print("handle_message", data)
        except Exception as e:
            pass

    def on_connect(self):
        print('[Connected]')

    def on_reconnect(self):
        print('[Reconnected]')

    def on_disconnect(self):
        print('[Disconnected]')

#https://pypi.org/project/socketIO-client/
class Streaming:

    def __init__(self, config: ConfigDTO = None, wait_for_connection = True):
        super().__init__()
        self.__config = copy.deepcopy(config)
        self.wait_for_connection = wait_for_connection
        self.q = queue.Queue(maxsize=1000)
        self.condition = Condition(RLock())
        self.started = False
        self.waiting = False
        self.socketIO = None

    def __build(self):
        #while True:
        data_auth = {'username': self.__config.streaming.username, 'password': self.__config.streaming.password}
        self.socketIO = SocketIO(host=self.__config.streaming.host, port=self.__config.streaming.port, Namespace=Namespace, wait_for_connection=self.wait_for_connection, params=data_auth)
        self.socketIO.wait(seconds=1)

    def __check_socket(self):
        if self.socketIO and self.socketIO.connected == False:
            self.socketIO.connect()

    def initialize(self):
        try:
            self.__build()
            self.__check_socket()
        except Exception as e:
            print(e)

    def __on_bbb_response(self, *args):
        print('on_bbb_response', args)
 
    def __process(self, item: StreamDTO = None) -> None:
        try:
            if item is None:
                return
            jpeg = item.image.tobytes()
            jpeg = base64.b64encode(jpeg).decode('utf-8')
            image = "data:image/jpeg;base64,{}".format(jpeg)
            item = {'image': True, 'source': item.source, 'buff': image, 'username': self.__config.streaming.username}
            self.__check_socket()
            if self.socketIO:
                self.socketIO.emit('handle_frame', item, callback=self.__on_bbb_response)
        except Exception as e:
            print(e)

    def __worker(self):
        while self.started == True:
            if self.q.empty() == True:
                with self.condition:
                    self.waiting = True
                    self.condition.wait()
                    self.waiting = False
            else:
                item = self.q.get()
                self.__process(item)
                self.q.task_done()

    def put_nowait(self, item: StreamDTO = None) -> None:
        global start_broadcasting
        if start_broadcasting > 1:
            self.q.put_nowait(item)
            self.run()
            if self.waiting == True:
                with self.condition:
                    self.condition.notify_all()

    def put(self, item: StreamDTO = None, block=True, timeout=None) -> None:
        global start_broadcasting
        if start_broadcasting > 1:
            self.q.put(item, block, timeout)
            self.run()
            if self.waiting == True:
                with self.condition:
                    self.condition.notify_all()

    def run(self) -> None:
        if self.started == True:
            return
        self.started = True
        self.thr = Thread(target=self.__worker, daemon=True)
        self.thr.start()

    def join(self) -> None:
        self.q.join()
    
    def __unsuscriber(self):
        if self.socketIO:
            #self.socketIO.emit('on_unsubscriber', callback=self.__on_bbb_response)
            self.socketIO.emit('unsubscriber', callback=self.__on_bbb_response)
            self.socketIO.wait_for_callbacks(seconds=1)
            self.socketIO.disconnect()

    def stop(self):
        self.started = False
        self.__unsuscriber()

    def __del__(self):
        self.__config = None
        self.q = None
        self.started = None
        self.socketIO = None
        self.condition = None
        self.waiting = None
        self.wait_for_connection = None
