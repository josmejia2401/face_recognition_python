import json
from app.utils.dir import get_data_config

def get_config():
    dir = get_data_config("config.json")
    with open(dir) as f:
        data = json.load(f)
    return data