#!/usr/bin/python3.8
#OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
import threading, queue
import boto3
from utils.settings import get_settings_aws, get_settings_alarm

class Alert:
    
    def __init__(self):
        super().__init__()
        self.q = queue.Queue()
        self.CURRENT_MOV = 0
        self.client = None
        self._build()
        self._RUNNING = False
        self.msg_send = 0
        

    def _build(self) -> None:
        # Read config
        self.setting_aws = get_settings_aws()
        self.setting_alarm = get_settings_alarm()
        # Create an SNS client
        if self.setting_aws["ACCES_KEY"]:
            self.client = boto3.client(
                "sns",
                aws_access_key_id=self.setting_aws["ACCES_KEY"],
                aws_secret_access_key=self.setting_aws["SECRET_KEY"],
                region_name=self.setting_aws["REGION_NAME"]
            )

    def _process_worker(self, item) -> None:
        # Send your sms message.
        try:
            if self.msg_send > int(self.setting_alarm["MAX_MSG"]):
                return
            self.CURRENT_MOV += 1
            if self.CURRENT_MOV > self.setting_alarm["MAX_MOV"] and self.client:
                phone_num = str(self.setting_alarm["INDICATOR"]) + str(self.setting_alarm["PHONE_NUMBER"]) 
                self.client.publish(PhoneNumber=phone_num, Message=item["message"])
                self.CURRENT_MOV = 0
                self.msg_send += 1
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

    def __del__(self):
        try:
            self.q = None
            self.setting_aws = None
            self.setting_alarm = None
            self.client = None
        except Exception as e:
            print(e)