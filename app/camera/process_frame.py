#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from app.dto.record import FrameDTO, StreamDTO, ConfigDTO
from app.camera.frame import Frame
from app.camera.record import Record
from app.camera.alert import Alert
from app.camera.q import Q
import copy
import time

class ProcessFrame(Q):
 
    def __init__(self, config: ConfigDTO = None):
        super().__init__()
        self.__config = copy.deepcopy(config)
        self.__frame = Frame(self.__config)
        self.__record = Record(self.__config)
        self.__alert = Alert(self.__config)

    def process_item(self, item: FrameDTO = None) -> None:
        try:
            if item is None:
                return
            is_mov = self.__frame.is_movement(item.frame1, item.frame2)
            stream_dto = StreamDTO(item.source, item.frame2, self.__config.camera.cameraType, is_mov, item.image)
            self.__record.put_item(stream_dto)
            self.__alert.put_item(stream_dto)
        except Exception as e:
            print("ProcessFrame__process", e)
    
    def process_status(self)-> None:
        try:
            if self.__config.general.delay_status > 0:
                time.sleep(self.__config.general.delay_status)
        except: pass

    def empty_queue_for_lock(self)-> None:
        if self.__config.general.delay > 0:
            time.sleep(self.__config.general.delay)
        else:
            self.apply_lock()

    def initialize(self):
        self.__record.initialize()
        self.__alert.initialize()
        self.run_queue()

    def stop(self) -> None:
        self.stop_queue()
        self.__record.stop()
        self.__alert.stop()