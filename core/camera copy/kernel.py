#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from camera.camera_async import CameraAsync
from camera.frame import Frame
from camera.record import Record
from camera.streaming import Streaming
from camera.type_cam import TypeCam
from dto.record import RecordDTO
from threading import Thread

class Kernel:

    def __init__(self, src=0):
        super().__init__()
        self.src = src
        self.__CAMERA = CameraAsync(src=self.src, name=str(self.src))
        self.started = False
    
    def __build__(self):
        width, height = self.__CAMERA.get_dimentions()
        self.__FRAME = Frame()
        self.__RECORD = Record(width, height)
        #self.__STREAMING = Streaming()

    def initialize(self):
        self.__CAMERA.initialize()
        self.__CAMERA.start()
        self.__build__()
        self.start()

    def stop(self, src=0) -> None:
        self.__CAMERA.stop()
        self.started = False
    
    def start(self) -> None:
        if self.started == True:
            return
        self.started = True
        #self.thread = Thread(target=self.__update, args=(), daemon=True)
        #self.thread.start()

    def __update(self) -> None:
        while self.started == True:
            try:
                pass
                #grabbed1, frame1, grabbed2, frame2 = self.__CAMERA.read()
                #if frame1 is None or frame2  is None:
                #    continue
                #grabbed, frame, is_mov = self.__FRAME.get_frame_normal(frame1, frame2)
                #_, jpg = self.__FRAME.get_stream_to_image(frame)
                #_r = RecordDTO(self.src, TypeCam.NORMAL, is_mov, frame, jpg)
                #self.__RECORD.put_nowait(_r)
                #self.__STREAMING.put_nowait(_r)
            except Exception as e:
                print(e)
    
