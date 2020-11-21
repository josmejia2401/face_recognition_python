#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from socketIO_client import SocketIO, BaseNamespace#, LoggingNamespace
from dto.record import StreamDTO, ConfigDTO
import base64
import copy

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
class Streaming:

    stop_transmission = True

    def __init__(self, config: ConfigDTO = None, wait_for_connection = True):
        super().__init__()
        self.__config = copy.deepcopy(config)
        self.wait_for_connection = wait_for_connection
        self.current_intents = 0
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
        #print('__on_response', args)
        pass

    def __subscribe(self):
        if self.socketIO:
            self.socketIO.emit('subscriber', callback=self.__on_response)
            self.socketIO.wait_for_callbacks(seconds=0.01)

    def __unsuscriber(self):
        if self.socketIO:
            self.socketIO.emit('unsubscriber', callback=self.__on_response)
            self.socketIO.wait_for_callbacks(seconds=1)
            self.socketIO.disconnect()

    def initialize(self):
        self.__connect(force=False)

    def send_data(self, item: StreamDTO = None) -> None:
        try:
            self.current_intents += 1
            if self.current_intents > 250:
                self.current_intents = 0
                self.__connect(force=True)
            else:
                self.__connect(force=False)
            if Streaming.stop_transmission == True:
                return
            if item is None:
                return
            item = self.__build_data(item)
            self.socketIO.emit('cv-data', item, callback=self.__on_response)
        except Exception as e:
            print(e)

    def stop(self):
        self.__unsuscriber()
        Streaming.stop_transmission = True

    def __del__(self):
        self.__config = None
        self.wait_for_connection = None
        self.socketIO = None
        self.data_auth = None
