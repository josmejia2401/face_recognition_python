#from https://dbader.org/blog/records-structs-and-data-transfer-objects-in-python
class StreamDTO:
    def __init__(self, source, frame, camera_type, is_mov, image):
        self.source = source
        self.frame = frame
        self.camera_type = camera_type
        self.is_mov = is_mov
        self.image = image
    
class FrameDTO:
    def __init__(self, source, frame1, frame2):
        self.source = source
        self.frame1 = frame1
        self.frame2 = frame2
#config
class GeneralDTO:
    def __init__(self, data_json = {}):
        self.maxMovements = int(data_json["MAX_MOVEMENTS"])
        self.onGuard = int(data_json["ON_GUARD"])
        self.minAreaObject = int(data_json["MIN_AREA_OBJECT"])

class AlarmDTO:
    def __init__(self, data_json = {}):
        self.phoneNumber = str(data_json["PHONE_NUMBER"])
        self.indicator = str(data_json["INDICATOR"])
        self.maxMessages = str(data_json["MAX_MESSAGES"])
        self.defaultMessage = str(data_json["DEFAULT_MESSAGE"])

class AwsDTO:
    def __init__(self, data_json = {}):
        self.accessKey = str(data_json["ACCESS_KEY"])
        self.secretKey = str(data_json["SECRET_KEY"])
        self.regionName = str(data_json["REGION_NAME"])

class CameraDTO:
    def __init__(self, data_json = {}):
        self.dimWidth = int(data_json["DIM_WIDTH"])
        self.dimHeight = int(data_json["DIM_HEIGHT"])
        self.cameraType = int(data_json["CAMERA_TYPE"])

class RecordDTO:
    def __init__(self, data_json = {}):
        self.fps = float(data_json["FPS"])
        self.maxTimeOutSeg = int(data_json["MAX_TIME_OUT_SEG"])

class ConfigDTO:
    def __init__(self, data_json = {}):
        self.general = GeneralDTO(data_json["GENERAL"])
        self.alarm = AlarmDTO(data_json["ALARM"])
        self.aws = AwsDTO(data_json["AWS"])
        self.camera = CameraDTO(data_json["CAMERA"])
        self.record = RecordDTO(data_json["RECORD"])