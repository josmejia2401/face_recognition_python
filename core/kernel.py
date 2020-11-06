#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from core.camera_async import CameraAsync
from core.frame import Frame
from core.record import Record
from threading import Thread

class Kernel:

    def __init__(self, src, name_src):
        super().__init__()
        self.__camera = CameraAsync(src=src, name=name_src)
        self.__frame = Frame()
        self.__record = Record()
        self.__running = False

    def initialize(self):
        self.__camera.initialize()
        self.__camera.start()
        width, height = self.__camera.get_dimentions()
        self.__record.initialize(width, height)

    def stop(self)->None:
        self.__running = False

    def stop_all(self)->None:
        self.stop() 
        self.__camera.stop()

    def background_start(self) -> None:
        if self.__running == True:
            return
        self.thread = Thread(target=self.__update, args=(), name=self.name, daemon=True)
        self.thread.start()

    def __update(self) -> None:
        while self.__running == False:
            grabbed1, frame1, grabbed2, frame2 = self.__camera.read()
            grabbed, frame, is_mov = self.__frame.get_frame_normal(frame1, frame2)
            self.__record.put_nowait({ "type_cam": 1, "is_mov": is_mov, "frame": frame })

    def generated_stream_diff(self):
        if self.__running == True:
            raise Exception("camera busy")
        if self.__camera.get_started() == False:
            self.initialize()
        self.__running = True
        while self.__running == True:
            grabbed1, frame1, grabbed2, frame2 = self.__camera.read()
            grabbed, frame, is_mov = self.__frame.get_frame_diff(frame1, frame2)
            self.__record.put_nowait({ "type_cam": 3, "is_mov": is_mov, "frame": frame })
            ret, jpeg = self.__frame.get_stream_to_image(frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    
    def generated_stream_mov(self):
        if self.__running == True:
            raise Exception("camera busy")
        if self.__camera.get_started() == False:
            self.initialize()
        self.__running = True
        while self.__running == True:
            grabbed1, frame1, grabbed2, frame2 = self.__camera.read()
            grabbed, frame, is_mov = self.__frame.get_frame_mov(frame1, frame2)
            self.__record.put_nowait({ "type_cam": 2, "is_mov": is_mov, "frame": frame })
            ret, jpeg = self.__frame.get_stream_to_image(frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    
    def generated_stream_normal(self):
        if self.__running == True:
            raise Exception("camera busy")
        if self.__camera.get_started() == False:
            self.initialize()
        self.__running = True
        while self.__running == True:
            grabbed1, frame1, grabbed2, frame2 = self.__camera.read()
            grabbed, frame, is_mov = self.__frame.get_frame_normal(frame1, frame2)
            self.__record.put_nowait({ "type_cam": 1, "is_mov": is_mov, "frame": frame })
            ret, jpeg = self.__frame.get_stream_to_image(frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    
    