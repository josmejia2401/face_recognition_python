#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from threading import Thread, Condition, Lock
import queue
import copy
from abc import ABC, abstractmethod
from dto.record import FrameDTO

class Q(ABC):

    def __init__(self, maxsize_queue = 1000, numbers_threads = 1, thread_status = False):
        super().__init__()
        self.__numbers_threads = numbers_threads
        self.__thread_status = thread_status
        self.__q = queue.Queue(maxsize=maxsize_queue)
        self.condition = Condition(Lock())
        self.waiting = False
        self.started = False
    
    @abstractmethod
    def process_item(self, item)-> None:
        pass
    
    @abstractmethod
    def empty_queue_for_lock(self)-> None:
        pass

    @abstractmethod
    def process_status(self)-> None:
        pass

    def apply_lock(self):
        if self.waiting == False:
            with self.condition:
                self.waiting = True
                self.condition.wait()
                self.waiting = False

    def apply_unlock(self):
        if self.waiting == True:
            with self.condition:
                self.condition.notify_all()

    def __worker(self):
        while self.started == True:
            try:
                if self.__q.empty() == True:
                    self.empty_queue_for_lock()
                else:
                    item = self.__q.get()
                    self.process_item(item)
                    self.__q.task_done()
            except: pass

    def __worker__status(self):
        while self.started == True:
            try:
                self.process_status()
            except: pass

    def q_values(self):
        return self.__q

    def put_nowait_item(self, item: FrameDTO = None) -> None:
        self.__q.put_nowait(item)
        self.apply_unlock()

    def put_item(self, item: FrameDTO = None, block=True, timeout=None) -> None:
        self.__q.put(item, block, timeout)
        self.apply_unlock()

    def run_queue(self) -> None:
        if self.started == True:
            return
        self.started = True
        self.threads = []
        for i in range(self.__numbers_threads):
            thr = Thread(target=self.__worker, daemon=True)
            thr.start()
            self.threads.append(thr)
        
        print("self.__thread_status", self.__thread_status)
        if self.__thread_status == True:
            thr = Thread(target=self.__worker__status, daemon=True)
            thr.start()
            self.threads.append(thr)

    def join_queue(self) -> None:
        self.__q.join()

    def stop_queue(self) -> None:
        self.started = False