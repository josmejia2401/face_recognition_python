import json
from utils.dir import get_data_settings

def get_settings_aws():
    dir = get_data_settings("aws.json")
    with open(dir) as f:
        data = json.load(f)
    return data

def get_settings_alarm():
    dir = get_data_settings("alarm.json")
    with open(dir) as f:
        data = json.load(f)
    return data

def get_settings_camera():
    dir = get_data_settings("camera.json")
    with open(dir) as f:
        data = json.load(f)
    return data

def get_settings_record():
    dir = get_data_settings("record.json")
    with open(dir) as f:
        data = json.load(f)
    return data