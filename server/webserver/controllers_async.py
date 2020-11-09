#!/usr/bin/python3.8
from core.kernel import Kernel

_k = Kernel(src=0)
_k.initialize()

def _video_feed() -> any:
    try:
        global _k
        if _k is None:
            _k = Kernel()
        return _k.generated_stream()
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        print(e)
        return str(e), 500

def _video_stop() -> any:
    try:
        global _k
        if _k is None:
            return "OK", 200
        _k.stop()
        return "OK", 200
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        print(e)
        return str(e), 500

def _video_stop_all() -> any:
    try:
        global _k
        if _k is None:
            return "OK", 200
        _k.stop_all()
        return "OK", 200
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        print(e)
        return str(e), 500