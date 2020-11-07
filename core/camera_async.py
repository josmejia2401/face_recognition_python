#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from core.frame import Frame
from core.record import Record
from dto.record import RecordDTO
from core.type_cam import TypeCam

import cv2
from threading import Thread, Lock
import time

class CameraAsync:

    def __init__(self, src=0, name='0', width=None, height=None):
        super().__init__()
        self.name = name
        self.src = src
        self.width=width
        self.height = height
        #others
        self.__running = False
        self.started = False
        self.read_lock = Lock()
        self.stream = None
        self.grabbed1, self.frame1 = None, None
        self.grabbed2, self.frame2 = None, None
        #dependencies
        self.__FRAME = Frame()
        self.__RECORD = Record()

    def __put_stream__(self) -> None:
        if self.stream and self.stream.isOpened():
            return
        self.stream = cv2.VideoCapture(self.src)
        if self.width is None or self.height is None:
            self.height = int(self.stream.get(3))
            self.width = int(self.stream.get(4))
        self.stream.set(3, self.height)
        self.stream.set(4, self.width)

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
    
    def initialize(self) -> None:
        self.__put_stream__()
        self.__RECORD.initialize(self.width, self.height)

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
    
    def __process(self):
        grabbed, frame, is_mov = self.__FRAME.get_frame_normal(self.frame1, self.frame2)
        _r = RecordDTO(self.src, TypeCam.NORMAL, is_mov, frame)
        self.__RECORD.put_nowait(_r)

    def __update(self) -> None:
        while self.started == True and self.stream.isOpened() == True:
            (grabbed, frame) = self.stream.read()
            #self.read_lock.acquire()
            with self.read_lock:
                if self.frame1 is None or self.frame2 is None:
                    self.grabbed1, self.frame1 = grabbed, frame
                else:
                    self.grabbed1, self.frame1 = self.grabbed2, self.frame2
                self.grabbed2, self.frame2 = grabbed, frame
                self.__process()
            #self.read_lock.release()
        
    def read(self) -> any:
        #self.read_lock.acquire()
        with self.read_lock:
            frame1 = self.frame1.copy()
            grabbed1 = self.grabbed1
            frame2 = self.frame2.copy()
            grabbed2 = self.grabbed2
            #self.read_lock.release()
            return grabbed1, frame1, grabbed2, frame2
    
    def generated_stream(self):
        #if self.__running == True:
        #    raise Exception("camera busy")
        if self.get_started() == False:
            self.initialize()
        self.__running = True
        while self.__running == True:
            _, frame1, _, frame2 = self.read()
            _, frame, _ = self.__FRAME.get_frame_normal(frame1, frame2)
            ret, jpeg = self.__FRAME.get_stream_to_image(frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    
    def stop_generated(self):
        self.__running = False

    def stop(self) -> any:
        try:
            self.stop_generated()
            self.started = False
            time.sleep(0.9)
            self.thread.join()
            self.release()
            self.grabbed1, self.frame1 = None, None
            self.grabbed2, self.frame2 = None, None
            self.stream = None
            self.__RECORD.stop()
        except Exception as e:
            print(e)

    def release(self):
        if self.stream:
            self.stream.release()
        self.__RECORD.release()
    
    def __exit__(self, exc_type, exc_value, traceback):
        print("exit")
        self.stop()
    
    def __del__(self):
        print("del")
        self.stop()
