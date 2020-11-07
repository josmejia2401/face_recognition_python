#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from dto.record import RecordDTO
from utils.settings import get_settings_record
import cv2
import datetime
import threading
import queue


class Record:

    def __init__(self):
        super().__init__()
        self.q = queue.Queue()
        self.fheight = None
        self.fwidth = None
        self.cont_frame = 0
        self.started = False
        self.stoped = False
        self.cont_frame_time_out = 0

    def initialize(self, fwidth, fheight):
        self.fheight = fheight
        self.fwidth = fwidth
        self.SETTINGS = get_settings_record()
        self.MAX_TIME_SEG = int(self.SETTINGS["MAX_TIME_SEG"])
        self.FPS = int(self.SETTINGS["FPS"])
        self.TIME_OUT_FRAME = self.FPS * 10 #10 segundos adicionales para grabar

    def __put_video_writter(self, src):
        time_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter('output_{}_{}.avi'.format(src, time_string), fourcc, self.FPS, (self.fheight, self.fwidth))

    #otorga 10s adicionales despuès de un movimiento,  es decir, si algo se muevo graba 10s mas esperando que se vuelva a mover.
    def __continue_record(self, item: RecordDTO = None):
        self.cont_frame += 1
        if item.is_mov == True:
            self.out.write(item.frame)
            self.cont_frame_time_out = self.cont_frame + self.TIME_OUT_FRAME
            if self.__check_release():
                self.release()
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

    def _process_worker(self, item: RecordDTO = None) -> None:
        try:
            if self.cont_frame == 0:
                self.__put_video_writter(src=item.src)
            self.__continue_record(item)
        except Exception as e:
            print(e)

    def _worker(self):
        while self.q.empty() == False and self.stoped == False:
            item = self.q.get()
            self._process_worker(item)
            self.q.task_done()
        self.started = False
        self.stoped = False

    def put_nowait(self, item: RecordDTO = None) -> None:
        self.q.put_nowait(item)
        self.run()

    def put(self, item: RecordDTO = None, block=True, timeout=None) -> None:
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

    def stop(self):
        self.stoped = True
        self.release()

    def release(self):
        self.out.release()
        self.cont_frame = 0
        self.cont_frame_time_out = 0

    def __del__(self):
        try:
            self.q = None
            self.SETTINGS = None
            self.release()
            self.out = None
        except Exception as e:
            print(e)
