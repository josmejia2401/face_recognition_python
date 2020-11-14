#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from dto.record import StreamDTO, ConfigDTO
import datetime
from threading import Thread, RLock, Condition
import cv2
import queue
import boto3
import copy

class RecordAndAlert:
 
    def __init__(self, config: ConfigDTO = None):
        super().__init__()
        self.__config = copy.deepcopy(config)
        self.q = queue.Queue(maxsize=2000)
        self.cont_frame = 0
        self.cont_frame_time_out = 0
        self.current_mov = 0
        self.started = False
        self.out = None
        self.client = None
        self.condition = Condition(RLock())
        self.__build()

    def __build(self):
        self.TIME_OUT_FRAME = self.__config.record.fps * 10 #10 segundos adicionales para grabar
        if self.__config.aws.accessKey:
            self.client = boto3.client("sns", 
                aws_access_key_id=self.__config.aws.accessKey, 
                aws_secret_access_key=self.__config.aws.secretKey, 
                region_name=self.__config.aws.regionName)
        
    def __put_video_writter(self, source):
        time_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        #fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        filename = 'output_{}_{}.avi'.format(str(source), time_string)
        frameSize = (self.__config.camera.dimWidth, self.__config.camera.dimHeight)
        self.out = cv2.VideoWriter(filename, fourcc, self.__config.record.fps, frameSize)


    #otorga 10s adicionales despuès de un movimiento,  es decir, si algo se muevo graba 10s mas esperando que se vuelva a mover.
    def __record(self, item: StreamDTO = None):
        self.cont_frame += 1
        if item.is_mov == True: 
            self.out.write(item.frame)
            self.cont_frame_time_out = self.cont_frame + self.TIME_OUT_FRAME
        else:
            if self.cont_frame_time_out == 0:
                self.cont_frame_time_out = self.cont_frame + self.TIME_OUT_FRAME
                self.out.write(item.frame)
            if self.cont_frame < self.cont_frame_time_out:
                self.out.write(item.frame)
            elif self.__check_release():
                self.release()
            else:
                self.release()

    #revisa si el video ya tiene el tamaño parametrizado
    def __check_release(self):
        current_time = int(self.cont_frame / self.__config.record.fps)
        if current_time > self.__config.record.maxTimeOutSeg:
            return True
        return False
    
    def __alert(self, item: StreamDTO = None):
        try:
            self.current_mov += 1
            if self.current_mov > self.__config.general.maxMovements and self.client:
                phoneNumber = self.__config.alarm.indicator + self.__config.alarm.phoneNumber
                self.client.publish(PhoneNumber=phoneNumber, Message=self.__config.alarm.defaultMessage)
                self.current_mov = 0
        except Exception as e:
            print(e)
            self.current_mov -= 1
        
    def __process(self, item: StreamDTO = None) -> None:
        try:
            if item is None:
                return
            if self.cont_frame == 0:
                self.__put_video_writter(item.source)
            self.__record(item)
            #self.__alert(item)
        except Exception as e:
            print(e)

    def __worker(self):
        while self.started == True:
            with self.condition:
                if self.q.empty() == True:
                    self.condition.wait()
                item = self.q.get()
                self.__process(item)
                self.q.task_done()
    
    def put_nowait(self, item: StreamDTO = None) -> None:
        self.q.put_nowait(item)
        self.run()
        with self.condition:
            self.condition.notify_all()

    def put(self, item: StreamDTO = None, block=True, timeout=None) -> None:
        self.q.put(item, block, timeout)
        self.run()
        with self.condition:
            self.condition.notify_all()

    def run(self) -> None:
        if self.started == True:
            return
        self.started = True
        self.thr = Thread(target=self.__worker, daemon=True)
        self.thr.start()

    def join(self) -> None:
        self.q.join()

    def stop(self):
        try:
            self.started = False
            self.release()
        except:
            pass

    def release(self):
        print("releaseeeeeeeeeeee")
        if self.out is not None:
            print("releaseeeeeeeeeeee 2222222")
            self.out.release()
            print("releaseeeeeeeeeeee 3333333")
        self.cont_frame = 0
        self.cont_frame_time_out = 0

    def __del__(self):
        self.__config = None
        self.q = None
        self.cont_frame = None
        self.cont_frame_time_out = None
        self.current_mov = 0
        self.started = None
        self.out = None
        self.client = None
        self.condition = None
        self.TIME_OUT_FRAME = None
        self.client = None
