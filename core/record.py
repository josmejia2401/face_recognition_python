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
        self._RUNNING = False
        self.fheight = None
        self.fwidth = None
        self.cont_frame = 0
        self.type_cam = None

    def set_dimentions(self, fheight, fwidth):
        self._build(fheight, fwidth)

    def _build(self, fheight, fwidth) -> None:
        if self.fheight and self.fwidth:
            return
        self.fheight = fheight
        self.fwidth = fwidth
        # Read config
        self.settings_record = get_settings_record()
        
    def put_video_writter(self):
        #record
        time_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter('output_{}_{}.avi'.format(self.type_cam, time_string), fourcc, int(self.settings_record["FPS"]), (self.fheight, self.fwidth))

    def _process_worker(self, item) -> None:
        # Send your sms message.
        try:
            if self.cont_frame == 0:
                self.type_cam = item["type_cam"]
                self.put_video_writter()
            if int(self.settings_record["ALWAYS_RECORD"]) == 1:
                self.cont_frame += 1
                if item["type_cam"] == self.type_cam:
                    self.out.write(item["frame"])
                else:
                    self.type_cam = item["type_cam"]
                    self.release()
            elif item["is_mov"] == True and item["ret"] == True:
                self.cont_frame += 1
                if item["type_cam"] == self.type_cam:
                    self.out.write(item["frame"])
                else:
                    self.type_cam = item["type_cam"]
                    self.release()
            current_time = int(self.cont_frame / int(self.settings_record["FPS"]))
            if current_time > int(self.settings_record["MAX_TIME_SEG"]):
                self.release()
        except Exception as e:
            print(e)
            
    def _worker(self):
        self._RUNNING = True
        while self.q.empty() == False:
            item = self.q.get()
            self._process_worker(item)
            self.q.task_done()
        self._RUNNING = False

    def put_nowait(self, item) -> None:
        self.q.put_nowait(item)
        if self._RUNNING == False:
            self.run()
    
    def put(self, item, block=True, timeout=None) -> None:
        self.q.put(item, block, timeout)
        if self._RUNNING == False:
            self.run()
    
    def run(self) -> None:
        # turn-on the worker thread
        thr = threading.Thread(target=self._worker, daemon=True)
        thr.start()
    
    def join(self) -> None:
        self.q.join()
        print('All work completed')
    
    def release(self):
        self.out.release()
        self.cont_frame = 0

    def __del__(self):
        try:
            self.q = None
            self.settings_record = None
            self.release()
            self.out = None
        except Exception as e:
            print(e)