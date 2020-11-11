#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from dto.record import RecordDTO
from utils.settings import get_config
import cv2
import datetime
from threading import Thread, RLock, Condition
import queue
import boto3

class RecordAndAlert:
 
    def __init__(self, fwidth = None, fheight = None):
        super().__init__()
        self.q = queue.Queue(maxsize=2000)
        self.fheight = int(fheight)
        self.fwidth = int(fwidth)
        self.cont_frame = 0
        self.cont_frame_time_out = 0
        self.CURRENT_MOV = 0
        self.started = False
        self.out = None
        self.client = None
        self.threads = []
        self.condition = Condition(RLock())
        self.__build()

    def __build(self):
        self.CONFIG = get_config()
        # VARIABLES
        self.MAX_TIME_SEG = int(self.CONFIG["RECORD"]["MAX_TIME_SEG"])
        self.FPS = int(self.CONFIG["RECORD"]["FPS"])
        self.MAX_MOV = int(self.CONFIG["ALARM"]["MAX_MOV"])
        self.PHONE_NUMBER = str(self.CONFIG["ALARM"]["INDICATOR"]) + str(self.CONFIG["ALARM"]["PHONE_NUMBER"])
        self.DEFUALT_MESSAGE = self.CONFIG["ALARM"]["DEFAULT_MESSAGE"]
        self.TIME_OUT_FRAME = self.FPS * 10 #10 segundos adicionales para grabar
        if self.CONFIG["AWS"]["ACCES_KEY"]:
            self.client = boto3.client("sns",
                aws_access_key_id=self.CONFIG["AWS"]["ACCES_KEY"],
                aws_secret_access_key=self.CONFIG["AWS"]["SECRET_KEY"],
                region_name=self.CONFIG["AWS"]["REGION_NAME"]
            )
        
    def __put_video_writter(self, src):
        time_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        filename = 'output_{}_{}.avi'.format(src, time_string)
        frameSize = (self.fheight, self.fwidth)
        fps = self.FPS
        self.out = cv2.VideoWriter(filename, fourcc, fps, frameSize)

    #otorga 10s adicionales despuès de un movimiento,  es decir, si algo se muevo graba 10s mas esperando que se vuelva a mover.
    def __record(self, item: RecordDTO = None):
        self.cont_frame += 1
        if item.is_mov == True:
            self.out.write(item.frame)
            self.cont_frame_time_out = self.cont_frame + self.TIME_OUT_FRAME
        else:
            if self.cont_frame_time_out == 0:
                self.cont_frame_time_out = self.cont_frame + self.TIME_OUT_FRAME
            if self.cont_frame < self.cont_frame_time_out:
                self.out.write(item.frame)
            elif self.__check_release():
                self.release()
            else:
                self.release()

    #revisa si el video ya tiene el tamaño parametrizado
    def __check_release(self):
        current_time = int(self.cont_frame / self.FPS)
        if current_time > self.MAX_TIME_SEG:
            return True
        return False
    
    def __alert(self, item: RecordDTO = None):
        try:
            self.CURRENT_MOV += 1
            if self.CURRENT_MOV > self.MAX_MOV and self.client:
                self.client.publish(PhoneNumber=self.PHONE_NUMBER, Message=self.DEFUALT_MESSAGE)
                self.CURRENT_MOV = 0
        except Exception as e:
            print(e)
            self.CURRENT_MOV -= 1
        
    def __process(self, item: RecordDTO = None) -> None:
        self.condition.acquire()
        try:
            if self.cont_frame == 0:
                self.__put_video_writter(src=item.src)
            self.__record(item)
            self.__alert(item)
        except Exception as e:
            print(e)
        finally:
            self.condition.release()

    def __worker(self):
        while self.started == True:
            if self.q.empty() == True:
                with self.condition:
                    self.condition.wait()
            try:
                item = self.q.get()
                if item:
                    self.__process(item)
            except:
                pass
            finally:
                self.q.task_done()
    
    def put_nowait(self, item: RecordDTO = None) -> None:
        self.q.put_nowait(item)
        self.run()
        with self.condition:
            self.condition.notify_all()

    def put(self, item: RecordDTO = None, block=True, timeout=None) -> None:
        self.q.put(item, block, timeout)
        self.run()
        with self.condition:
            self.condition.notify_all()

    def run(self) -> None:
        if self.started == True:
            return
        self.started = True
        self.threads = []
        for i in range(1):
            thr = Thread(target=self.__worker, daemon=True)
            thr.start()
            self.threads.append(thr)

    def join(self) -> None:
        self.q.join()

    def stop(self):
        self.started = False
        self.release()

    def release(self):
        if self.out:
            self.out.release()
        self.cont_frame = 0
        self.cont_frame_time_out = 0

    def __del__(self):
        try:
            self.q = None
            self.CONFIG = None
            self.release()
            self.out = None
        except Exception as e:
            print(e)
