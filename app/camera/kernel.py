#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from app.camera.camera import CameraAsync

class Kernel:

    def __init__(self):
        super().__init__()
        self.__CAMERA = CameraAsync()
        self.__is_stop_streaming = False

    def initialize(self):
        self.__CAMERA.initialize()
        self.__CAMERA.start()

    def stop(self) -> None:
        self.__CAMERA.stop()

    def stop_streaming(self):
        self.__is_stop_streaming = True

    def get_frame(self):
        self.__is_stop_streaming = False
        while self.__is_stop_streaming == False:
            frame = self.__CAMERA.read()
            if frame is not None:
                frame = frame.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')