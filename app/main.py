#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
from app.camera.kernel import Kernel
import time
if __name__ == '__main__':
    try:
        _k = Kernel()
        _k.initialize()
        while True:
            time.sleep(1)
    except SystemExit as e:
        print(e)
        _k.stop()
    except KeyboardInterrupt as e:
        print(e)
        _k.stop()
    except Exception as e:
        print(e)
        _k.stop()