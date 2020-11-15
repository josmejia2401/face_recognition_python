#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
import copy
import boto3
import datetime
import cv2
from dto.record import ConfigDTO, StreamDTO

class Record:

    def __init__(self, config: ConfigDTO = None):
        super().__init__()
        self.__config = copy.deepcopy(config)
        self.cont_frame = 0
        self.cont_frame_time_out = 0
        self.time_out_frame = 0
        self.__build()

    def __build(self):
        self.time_out_frame = int(self.__config.record.fps * 10) #10 segundos adicionales para grabar

    def __put_video_writter(self, source):
        time_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        filename = 'output_{}_{}.avi'.format(str(source), time_string)
        frameSize = (self.__config.camera.dimWidth, self.__config.camera.dimHeight)
        self.out = cv2.VideoWriter(filename, fourcc, self.__config.record.fps, frameSize)
    
    def record(self, item: StreamDTO = None):
        if self.cont_frame == 0:
            self.__put_video_writter(item.source)
        self.__write(item)
        
    def __write(self, item: StreamDTO = None):
        self.cont_frame += 1
        if item.is_mov == True: 
            self.out.write(item.frame)
            self.cont_frame_time_out = self.cont_frame + self.time_out_frame
        else:
            if self.cont_frame_time_out == 0:
                self.cont_frame_time_out = self.cont_frame + self.time_out_frame
                self.out.write(item.frame)
            if self.cont_frame < self.cont_frame_time_out:
                self.out.write(item.frame)
            elif self.__check_size_for_release():
                self.release()
            else:
                self.release()

    def __check_size_for_release(self):
        current_time = int(self.cont_frame / self.__config.record.fps)
        if current_time > self.__config.record.maxTimeOutSeg:
            return True
        return False

    def release(self):
        print("release")
        if self.out is not None:
            self.out.release()
        self.cont_frame = 0
        self.cont_frame_time_out = 0
    
    def __del__(self):
        self.__config = None
        self.cont_frame = None
        self.cont_frame_time_out = None
        self.out = None
        self.time_out_frame = None
