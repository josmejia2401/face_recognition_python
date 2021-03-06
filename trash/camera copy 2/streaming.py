#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from socketIO_client import SocketIO, BaseNamespace#, LoggingNamespace
from dto.record import StreamDTO, ConfigDTO
import base64
import copy
from camera.q import Q
import time

class Namespace(BaseNamespace):

    def on_stream_video(self, data):
        print("on_stream_video", data)
        if data is None:
            return
        if isinstance(data, str) or isinstance(data, int):
            value = int(data)
            if value > 1:
                Streaming.stop_transmission = False
            else:
                Streaming.stop_transmission = True

    def on_connect(self):
        print('[Connected]')

    def on_reconnect(self):
        print('[Reconnected]')

    def on_disconnect(self):
        print('[Disconnected]')

#https://pypi.org/project/socketIO-client/
class Streaming(Q):

    stop_transmission = True

    def __init__(self, config: ConfigDTO = None, wait_for_connection = True):
        super().__init__(thread_status = True)
        self.__config = copy.deepcopy(config)
        self.wait_for_connection = wait_for_connection
        self.socketIO = None
        self.data_auth = {'username': self.__config.streaming.username, 'password': self.__config.streaming.password}
    
    def __connect(self, force = False):
        try:
            if self.socketIO is None:
                self.socketIO = SocketIO(host=self.__config.streaming.host, port=self.__config.streaming.port, Namespace=Namespace, wait_for_connection=self.wait_for_connection, params=self.data_auth)
                self.socketIO.wait(seconds=1)
                self.__subscribe()
            elif self.socketIO and self.socketIO.connected == False:
                self.socketIO.connect()
                self.socketIO.wait(seconds=1)
                self.__subscribe()
            if force == True:
                self.__subscribe()
        except Exception as e:
            raise e

    def __build_data(self, item: StreamDTO = None):
        try:
            jpeg = item.image.tobytes()
            jpeg = base64.b64encode(jpeg).decode('utf-8')
            image = "data:image/jpeg;base64,{}".format(jpeg)
            item = {'image': True, 'source': item.source, 'buff': image}
            return item
        except Exception as e:
            raise e
    
    def __on_response(self, *args):
        pass

    def __subscribe(self):
        if self.socketIO:
            self.socketIO.emit('subscriber', callback=self.__on_response)
            self.socketIO.wait_for_callbacks(seconds=1)

    def __unsuscriber(self):
        if self.socketIO:
            self.socketIO.emit('unsubscriber', callback=self.__on_response)
            self.socketIO.wait_for_callbacks(seconds=1)
            self.socketIO.disconnect()

    def process_item(self, item: StreamDTO = None) -> None:
        try:
            if Streaming.stop_transmission == True:
                return
            if item is None:
                return
            item = self.__build_data(item)
            self.__connect(force=False)
            self.socketIO.emit('cv-data', item, callback=self.__on_response)
        except Exception as e:
            print("Streaming__process_item", e)
        
    def empty_queue_for_lock(self)-> None:
        if self.__config.streaming.delay > 0:
            time.sleep(self.__config.streaming.delay)
        else:
            self.apply_lock()

    def process_status(self)-> None:
        try:
            self.__connect(force=True)
            if self.__config.streaming.delay_status > 0:
                time.sleep(self.__config.streaming.delay_status)
        except Exception as e:
            print("Streaming__process_status", e)

    def initialize(self):
        self.__connect(force=False)
        self.run_queue()

    def stop(self) -> None:
        self.stop_queue()
        self.__unsuscriber()
        Streaming.stop_transmission = True
