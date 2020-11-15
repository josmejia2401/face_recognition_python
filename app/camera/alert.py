#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
import copy
import boto3
from dto.record import ConfigDTO, StreamDTO

class Alert:

    def __init__(self, config: ConfigDTO = None):
        super().__init__()
        self.__config = copy.deepcopy(config)
        self.current_mov = 0
        self.client = None
        self.__build()

    def __build(self):
        if self.__config.aws.accessKey and self.__config.aws.secretKey and self.__config.aws.regionName:
            self.client = boto3.client(self.__config.aws.client, 
                aws_access_key_id=self.__config.aws.accessKey, 
                aws_secret_access_key=self.__config.aws.secretKey, 
                region_name=self.__config.aws.regionName)

    def alert(self, item: StreamDTO = None):
        try:
            if item.is_mov == True:
                self.current_mov += 1
                if self.current_mov > self.__config.general.maxMovements and self.client:
                    phoneNumber = self.__config.alarm.indicator + self.__config.alarm.phoneNumber
                    self.client.publish(PhoneNumber=phoneNumber, Message=self.__config.alarm.defaultMessage)
                    self.current_mov = 0
        except Exception as e:
            print(e)
    
    def __del__(self):
        self.__config = None
        self.current_mov = None
        self.client = None