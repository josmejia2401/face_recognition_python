#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from socketIO_client import SocketIO, LoggingNamespace
from dto.record import StreamDTO, ConfigDTO
from threading import Thread
import queue
import base64
import time
import copy

#https://pypi.org/project/socketIO-client/
class Streaming:

    def __init__(self, config: ConfigDTO = None, wait_for_connection = True):
        super().__init__()
        self.__config = copy.deepcopy(config)
        self.wait_for_connection = wait_for_connection
        self.q = queue.Queue(maxsize=1000)
        self.started = False
        self.socketIO = None
        self.is_send_frame = 0

    def __build(self):
        self.socketIO = SocketIO(host=self.__config.streaming.host, 
            port=self.__config.streaming.port, 
            Namespace=LoggingNamespace, 
            wait_for_connection=self.wait_for_connection)

    def __check_socket(self):
        if self.socketIO and self.socketIO.connected == False:
            self.socketIO.connect()

    def initialize(self):
        try:
            self.__build()
            self.__check_socket()
            self.__subscriber()
        except Exception as e:
            print(e)

    def __on_bbb_response(self, *args):
        print('on_bbb_response', args)

    def __send(self, item: StreamDTO = None) -> None:
        try:
            time.sleep(0.05)
            jpeg = item.image.tobytes()
            jpeg = base64.b64encode(jpeg).decode('utf-8')
            image = "data:image/jpeg;base64,{}".format(jpeg)
            item = {'image': True, 'source': item.source, 'buff': image, 'user': self.__config.streaming.user}
            self.__check_socket()
            if self.socketIO:
                self.socketIO.emit('on_frame', item, callback=self.__on_bbb_response)
        except Exception as e:
            print(e)

    def _worker(self):
        while self.started == True and self.q.empty() == False:
            item = self.q.get()
            if self.is_send_frame == 1:
                self.__send(item)
            else:
                time.sleep(1.5)
            self.q.task_done()
        self.started = False

    def put_nowait(self, item: StreamDTO = None) -> None:
        if self.is_send_frame == 1:
            self.q.put_nowait(item)
            self.run()

    def put(self, item: StreamDTO = None, block=True, timeout=None) -> None:
        if self.is_send_frame == 1:
            self.q.put(item, block, timeout)
            self.run()

    def run(self) -> None:
        if self.started == True:
            return
        self.started = True
        self.thr = Thread(target=self._worker, daemon=True)
        self.thr.start()

    def join(self) -> None:
        self.q.join()
    
    def __subscriber(self):
        self.__check_socket()
        self.socketIO.emit('on_subscriber', callback=self.on_bbb_response)
        self.socketIO.on('on_process_frame', self.__on_process_frame)
    
    def __on_process_frame(self, *args):
        print("data", *args)
        self.is_send_frame = int(*args)

    def __unsuscriber(self):
        if self.socketIO and self.socketIO.connected == True:
            self.socketIO.emit('on_unsubscriber', callback=self.on_bbb_response)
            self.socketIO.disconnect()

    def stop(self):
        self.started = False
        self.__unsuscriber()

    def __del__(self):
        self.__config = None
        self.q = None
        self.started = None
        self.socketIO = None
        self.is_send_frame = None
