#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from socketIO_client import SocketIO, LoggingNamespace
from dto.record import RecordDTO
import threading
import queue
import base64

#https://pypi.org/project/socketIO-client/
class Streaming:

    def __init__(self):
        super().__init__()
        self.q = queue.Queue(maxsize=1000)
        self.socketIO = SocketIO('localhost', 5000, LoggingNamespace)
        self.socketIO.wait()

    def initialize(self):
        item = {'user':'sucam'}
        self.socketIO.on('join', item)

    def __send(self, item: RecordDTO = None) -> None:
        try:
            jpeg = base64.b64encode(item.jpg).decode('utf-8')
            image = "data:image/jpeg;base64,{}".format(jpeg)
            self.socketIO.on('on_frame', (item.src, image))
        except Exception as e:
            print(e)

    def _worker(self):
        while self.started == True and self.q.empty() == False:
            item = self.q.get()
            self.__send(item)
            self.q.task_done()
        self.started = False

    def put_nowait(self, item: RecordDTO = None) -> None:
        self.q.put_nowait(item)
        self.run()

    def put(self, item: RecordDTO = None, block=True, timeout=None) -> None:
        self.q.put(item, block, timeout)
        self.run()

    def run(self) -> None:
        if self.started == True:
            return
        self.started = True
        self.thr = threading.Thread(target=self._worker, daemon=True)
        self.thr.start()

    def join(self) -> None:
        self.q.join()

    def stop(self):
        self.started = False

    def __del__(self):
        try:
            self.q = None
            self.socketIO.on('leave')
            self.socketIO = None
        except Exception as e:
            print(e)
