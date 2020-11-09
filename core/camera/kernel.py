#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from camera.camera_async import CameraAsync

class Kernel:

    def __init__(self, src=0):
        super().__init__()
        self.src = src
        self.__CAMERA = CameraAsync(src=self.src, name=str(self.src))

    def initialize(self):
        self.__CAMERA.initialize()
        self.__CAMERA.start()

    def stop(self, src=0) -> None:
        self.__CAMERA.stop()