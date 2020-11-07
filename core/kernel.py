#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from core.camera_async import CameraAsync

class Kernel:

    def __init__(self, src = None):
        super().__init__()
        self.src = src
        self.__build__()
    
    def __build__(self):
        self.__list_availables_devices = []
        for src in CameraAsync.list_devices():
            _camera = CameraAsync(src=src, name=str(src))
            if self.src is None:
                self.__list_availables_devices.append(_camera)
            elif self.src == src:
                self.__list_availables_devices.append(_camera)
                break

    def initialize(self):
        for item in self.__list_availables_devices:
            item.initialize()
            item.start()

    def stop(self, src=0)->None:
        for item in self.__list_availables_devices:
            if item.src == src:
                item.stop_generated()
                break

    def stop_all(self, src=0)->None:
        self.stop(src)
        for item in self.__list_availables_devices:
            if item.src == src:
                item.stop()
                break

    def generated_stream(self, src=0):
        cam = None
        for item in self.__list_availables_devices:
            if item.src == src:
                cam = item
                break
        return cam.generated_stream()