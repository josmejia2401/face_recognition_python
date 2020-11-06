#!/usr/bin/python3.8
#OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
import threading, queue
from utils.settings import get_settings_record
import cv2
import datetime

class Record:
    
    def __init__(self):
        super().__init__()
        self.q = queue.Queue()
        self.fheight = None
        self.fwidth = None
        self.cont_frame = 0
        self.type_cam = None
        self.started = False

    def initialize(self, fwidth, fheight):
        self.fheight = fheight
        self.fwidth = fwidth
        self.SETTINGS = get_settings_record()
        
    def __put_video_writter(self):
        #record
        time_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter('output_{}_{}.avi'.format(self.type_cam, time_string), fourcc, int(self.SETTINGS["FPS"]), (self.fheight, self.fwidth))

    def _process_worker(self, item) -> None:
        # Send your sms message.
        try:
            type_cam = item["type_cam"]
            is_mov = item["is_mov"]
            frame = item["frame"]

            if self.cont_frame == 0:
                self.type_cam = type_cam
                self.__put_video_writter()

            if is_mov == True:
                self.cont_frame += 1
                if type_cam == self.type_cam:
                    self.out.write(frame)
                else:
                    self.type_cam = type_cam
                    self.release()
            # process
            current_time = int(self.cont_frame / int(self.SETTINGS["FPS"]))
            if current_time > int(self.SETTINGS["MAX_TIME_SEG"]):
                self.release()
        except Exception as e:
            print(e)
            
    def _worker(self):
        while self.q.empty() == False:
            item = self.q.get()
            self._process_worker(item)
            self.q.task_done()
        self.started = False

    def put_nowait(self, item) -> None:
        self.q.put_nowait(item)
        self.run()
    
    def put(self, item, block=True, timeout=None) -> None:
        self.q.put(item, block, timeout)
        self.run()
    
    def run(self) -> None:
        if self.started == True:
            return
        self.started = True
        self.thr = threading.Thread(target=self._worker, daemon=True)
        self.thr.start()
    
    def join(self) -> None:
        self.q.join()
        print('All work completed')
    
    def release(self):
        self.out.release()
        self.cont_frame = 0

    def __del__(self):
        try:
            self.q = None
            self.SETTINGS = None
            self.release()
            self.out = None
        except Exception as e:
            print(e)