#!/usr/bin/python3.8
from core.camera import Camera

_camera = Camera()

def _release():
    global _camera
    if _camera is None:
        return "OK", 200
    _camera.release()

def _video_feed(type_cam) -> any:
    try:
        global _camera
        if _camera is None:
            _camera = Camera()
        return _camera.generated_stream(type_cam)
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        print(e)
        return str(e), 500

def _video_stop(id=None) -> any:
    try:
        global _camera
        if _camera is None:
            return "OK", 200
        _camera.release()
        return "OK", 200
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        print(e)
        return str(e), 500