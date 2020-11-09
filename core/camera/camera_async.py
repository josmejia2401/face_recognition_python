#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
import cv2
from threading import Thread, Lock
import time
#internal
from camera.frame import Frame
from camera.record import Record
from camera.streaming import Streaming
from camera.type_cam import TypeCam
from dto.record import RecordDTO

class CameraAsync:

    def __init__(self, src=0, name='0', width=None, height=None):
        super().__init__()
        self.name = name
        self.src = src
        self.width=width
        self.height = height
        #others
        self.started = False
        self.read_lock = Lock()
        self.stream = None
        self.grabbed1, self.frame1 = None, None
        self.grabbed2, self.frame2 = None, None
        self.thread = None
        
    def __put_stream__(self) -> None:
        if self.stream and self.stream.isOpened():
            return
        self.stream = cv2.VideoCapture(self.src)
        if self.width is None or self.height is None:
            self.height = int(self.stream.get(3))
            self.width = int(self.stream.get(4))
        self.stream.set(3, self.height)
        self.stream.set(4, self.width)
    
    def initialize(self) -> None:
        self.__STREAMING = Streaming()
        self.__put_stream__()
        width, height = self.get_dimentions()
        self.__FRAME = Frame()
        self.__RECORD = Record(width, height)
        
    def get_started(self) -> bool:
        return self.started
    
    def get_dimentions(self):
        return self.width, self.height

    def start(self) -> None:
        if self.started == True:
            return
        self.started = True
        self.thread = Thread(target=self.__update, args=(), name=self.name, daemon=True)
        self.thread.start()

    def __update(self) -> None:
        while self.started == True and self.stream.isOpened() == True:
            (grabbed, frame) = self.stream.read()
            try:
                self.read_lock.acquire()
                self.__process(grabbed, frame)
            finally:
                self.read_lock.release()
    
    def __process(self, grabbed, frame):
        if self.frame1 is None or self.frame2 is None:
            self.grabbed1, self.frame1 = grabbed, frame
        else:
            self.grabbed1, self.frame1 = self.grabbed2, self.frame2
        self.grabbed2, self.frame2 = grabbed, frame
        grabbed, frame, is_mov = self.__FRAME.get_frame_normal(self.frame1, self.frame2)
        _, image = self.__FRAME.get_stream_to_image(frame)
        _r = RecordDTO(self.src, TypeCam.NORMAL, is_mov, frame, image)
        self.__RECORD.put_nowait(_r)
        self.__STREAMING.put_nowait(_r)

        
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
            self.thread.join()
            self.release()
            self.grabbed1, self.frame1 = None, None
            self.grabbed2, self.frame2 = None, None
            self.stream = None
        except Exception as e:
            print(e)

    def release(self):
        if self.stream:
            self.stream.release()
    
    @staticmethod
    def list_devices():
        index = 0
        arr = []
        cap = None
        while True:
            try:
                cap = cv2.VideoCapture(index)
                if not cap.read()[0]:
                    break
                else:
                    arr.append(index)
                cap.release()
                index += 1
            except Exception as e:
                print(e)
                cap.release()
        return arr

    def __exit__(self, exc_type, exc_value, traceback):
        print("exit")
        self.stop()
    
    def __del__(self):
        print("del")
        self.stop()
