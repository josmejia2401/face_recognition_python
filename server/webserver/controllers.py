#!/usr/bin/python3.8
from app.camera.kernel import Kernel

_k = Kernel()
_k.initialize()

def __stop_all() -> any:
    try:
        global _k
        if _k:
            _k.stop_streaming()
            _k.stop()
            return "OK", 200
        return None
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        print(e)
        return str(e), 500

def _video_feed() -> any:
    try:
        global _k
        if _k:
            return _k.get_frame()
        return None
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        print(e)
        return str(e), 500

def _video_stop() -> any:
    try:
        global _k
        if _k:
            _k.stop_streaming()
            return "OK", 200
        return None
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        print(e)
        return str(e), 500

def _video_reset() -> any:
    try:
        global _k
        if _k:
            _k.stop()
            _k = Kernel()
            _k.initialize()
            return "OK", 200
        return None
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        print(e)
        return str(e), 500