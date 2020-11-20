#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from dto.record import FrameDTO, StreamDTO, ConfigDTO
from camera.frame import Frame
from camera.record import Record
from camera.alert import Alert
from camera.streaming import Streaming
from threading import Thread, RLock, Condition
import queue
import copy
import time

class ProcessFrame:
 
    def __init__(self, config: ConfigDTO = None):
        super().__init__()
        self.__config = copy.deepcopy(config)
        self.q = queue.Queue(maxsize=1000)
        self.threads = []
        self.condition = Condition(RLock())
        self.THREADS_NUM = 1
        self.started = False
        self.waiting = False
        self.__build()

    def __build(self): 
        self.__frame = Frame(self.__config)
        self.__record = Record(self.__config)
        self.__alert = Alert(self.__config)
        self.__streaming = Streaming(self.__config, False)

    def __process(self, item: FrameDTO = None) -> None:
        try:
            if item is None:
                return
            is_mov = self.__frame.is_movement(item.frame1, item.frame2)
            new_frame = self.__frame.resize(item.frame1)
            _, image = self.__frame.frame_to_image(new_frame)
            stream_dto = StreamDTO(item.source, new_frame, self.__config.camera.cameraType, is_mov, image)
            self.__record.record(stream_dto)
            self.__alert.alert(stream_dto)
            self.__streaming.put_nowait(stream_dto)
        except Exception as e:
            print("__process", e)

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
                #time.sleep(0.1)

    def initialize(self):
        self.__streaming.initialize()
    
    def put_nowait(self, item: FrameDTO = None) -> None:
        self.q.put_nowait(item)
        self.run()
        if self.waiting == True:
            with self.condition:
                self.condition.notify_all()

    def put(self, item: FrameDTO = None, block=True, timeout=None) -> None:
        self.q.put(item, block, timeout)
        self.run()
        if self.waiting == True:
            with self.condition:
                self.condition.notify_all()

    def run(self) -> None:
        if self.started == True:
            return
        self.started = True
        self.threads = []
        for i in range(self.THREADS_NUM):
            thr = Thread(target=self.__worker, daemon=True)
            thr.start()
            self.threads.append(thr)

    def join(self) -> None:
        self.q.join()

    def stop(self) -> None:
        self.started = False
        self.__record.release()
        self.__streaming.stop()

    def __del__(self):
        self.__config = None
        self.q = None
        self.threads = None
        self.condition = None
        self.THREADS_NUM = None
        self.__frame = None
        self.__record = None
        self.__alert = None
        self.__streaming = None
