#from https://dbader.org/blog/records-structs-and-data-transfer-objects-in-python
class RecordDTO:
    def __init__(self, src, type_c, is_mov, frame):
        self.type_c = type_c
        self.is_mov = is_mov
        self.frame = frame
        self.src = src


class DeviceDTO:
    def __init__(self, cam, record, frame):
        self.camera = cam
        self.record = record
        self.frame = frame