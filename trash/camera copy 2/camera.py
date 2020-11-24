#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
import cv2
from threading import Thread, Lock
import time
#internal
from utils.settings import get_config
from dto.record import FrameDTO, ConfigDTO
from camera.process_frame import ProcessFrame

class CameraAsync:

    def __init__(self, source=0, name='thread-stream-0'):
        super().__init__()
        self.name = name
        self.source = source 
        self.__config = ConfigDTO(get_config())
        self.started = False
        self.read_lock = Lock()
        self.stream = None
        self.grabbed1, self.frame1 = None, None
        self.grabbed2, self.frame2 = None, None
        self.thread = None
        
    def __build(self) -> None:
        if self.stream and self.stream.isOpened():
            return
        self.__process_frame = ProcessFrame(self.__config)
        self.__process_frame.initialize()
        self.stream = cv2.VideoCapture(self.source)
        if self.__config.camera.dimHeight == 0 or self.__config.camera.dimWidth == 0:
            self.__config.camera.dimWidth = int(self.stream.get(3))
            self.__config.camera.dimHeight = int(self.stream.get(4))
            self.__config.camera.defaultDim = True
        else:
            self.__config.camera.defaultDim = False
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.__config.camera.dimWidth))
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.__config.camera.dimHeight))
    
    def initialize(self) -> None:
        self.__build()
        
    def get_started(self) -> bool:
        return self.started
    
    def start(self) -> None:
        if self.started == True:
            return
        self.started = True
        self.thread = Thread(target=self.__update, args=(), name=self.name, daemon=True)
        self.thread.start()

    def __update(self) -> None:
        while self.started == True and self.stream.isOpened() == True:
            (grabbed, frame) = self.stream.read()
            while grabbed == False: (grabbed, frame) = self.stream.read()
            self.__process(grabbed, frame)
    
    def __process(self, grabbed, frame):
        if self.frame1 is None or self.frame2 is None:
            self.grabbed1, self.frame1 = grabbed, frame
        else:
            self.grabbed1, self.frame1 = self.grabbed2, self.frame2
        self.grabbed2, self.frame2 = grabbed, frame
        frame_dto = FrameDTO(self.source, self.frame1, self.frame2)
        self.__process_frame.put_item(frame_dto)
        
    def read(self) -> any:
        try:
            self.read_lock.acquire()
            frame1 = self.frame1.copy()
            grabbed1 = self.grabbed1
            frame2 = self.frame2.copy()
            grabbed2 = self.grabbed2
        except Exception as e:
            grabbed1, frame1, grabbed2, frame2 = False, None, False, None
        finally:
            self.read_lock.release()
        return grabbed1, frame1, grabbed2, frame2

    def stop(self) -> any:
        try:
            self.started = False
            time.sleep(0.9)
            if self.thread:
                self.thread.join()
            self.release()
            self.__process_frame.stop()
        except Exception as e:
            print(e)

    def release(self):
        if self.stream:
            self.stream.release()

    def __exit__(self, exc_type, exc_value, traceback):
        print("exit")
    
    def __del__(self):
        self.started = None
        self.grabbed1, self.frame1 = None, None
        self.grabbed2, self.frame2 = None, None
        self.stream = None
        self.name = None
        self.source = None
        self.__config = None
        self.read_lock = None
        self.thread = None
