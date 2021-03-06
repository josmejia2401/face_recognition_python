#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from camera.camera import CameraAsync

class Kernel:

    def __init__(self):
        super().__init__()
        self.__CAMERA = CameraAsync()

    def initialize(self):
        self.__CAMERA.initialize()
        self.__CAMERA.start()

    def stop(self) -> None:
        self.__CAMERA.stop()