#!/usr/bin/python3.8
#OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
import cv2
import numpy as np
import time
from utils.dir import get_data_xml
from utils.settings import get_settings_camera
from core.alert import Alert
from core.record import Record

class Camera:

    def __init__(self, cam_id = 0, on_guard = False):
        super().__init__()
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.on_guard = on_guard
        #cam and dimentions
        self.cam_id = cam_id
        self.cam = None
        self.frame1 = None
        self.frame2 = None
        self.RELEASE_CAM = False
        self._ALERT = Alert()
        self._RECORD = Record()

    #initialize
    def initialize(self):
        self.settings_camera = get_settings_camera()
        self.RELEASE_CAM = False
        if self.cam and self.cam.isOpened():
            return
        elif self.cam:
            self.clear()
        self._put_cam_video()

    def _put_cam_video(self):
        self.cam = cv2.VideoCapture(self.cam_id)
        fheight = int(self.cam.get(3))
        fwidth = int(self.cam.get(4))
        self.cam.set(3,fheight)
        self.cam.set(4,fwidth)
        self._RECORD.set_dimentions(fheight, fwidth)

    def _get_frame_gray(self, frame1, frame2):
        # Difference between frame1(image) and frame2(image)
        diff = cv2.absdiff(frame1, frame2)
        # Converting color image to gray_scale image
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        return gray
    
    def _get_frame_diff(self, frame1, frame2):
        # Difference between frame1(image) and frame2(image)
        diff = cv2.absdiff(frame1, frame2)
        # Converting color image to gray_scale image
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        # Converting gray scale image to GaussianBlur, so that change can be find easily
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # If pixel value is greater than 20, it is assigned white(255) otherwise black
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        return thresh

    def _get_contours(self, frame1, frame2):
        # Difference between frame1(image) and frame2(image)
        diff = cv2.absdiff(frame1, frame2)
        # Converting color image to gray_scale image
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        # Converting gray scale image to GaussianBlur, so that change can be find easily
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # If pixel value is greater than 20, it is assigned white(255) otherwise black
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=4)
        # finding contours of moving object
        contours, hirarchy = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours, hirarchy

    def get_frame_gray(self):
        if self.frame1 is None:
            _, self.frame1 = self.cam.read()
        elif self.frame2 is None:
            _, self.frame1 = self.cam.read()
        else:
            self.frame1 = self.frame2
        ret, self.frame2 = self.cam.read()
        contours, hirarchy = self._get_contours(self.frame1, self.frame2)
        is_mov = False
        # making rectangle around moving object
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            referenceArea = self._is_object(contour)
            if referenceArea is None:
                continue
            is_mov = True
            break
        frame = self._get_frame_gray(self.frame1, self.frame2)
        self._process_mov(4, is_mov, ret, frame)
        return frame

    def get_frame_diff(self):
        if self.frame1 is None:
            _, self.frame1 = self.cam.read()
        elif self.frame2 is None:
            _, self.frame1 = self.cam.read()
        else:
            self.frame1 = self.frame2
        ret, self.frame2 = self.cam.read()
        contours, hirarchy = self._get_contours(self.frame1, self.frame2)
        is_mov = False
        # making rectangle around moving object
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            referenceArea = self._is_object(contour)
            if referenceArea is None:
                continue
            is_mov = True
            break
        frame = self._get_frame_diff(self.frame1, self.frame2)
        self._process_mov(3, is_mov, ret, frame)
        return frame

    def get_frame_normal(self):
        if self.frame1 is None:
            _, self.frame1 = self.cam.read()
        elif self.frame2 is None:
            _, self.frame1 = self.cam.read()
        else:
            self.frame1 = self.frame2
        frame = cv2.flip(self.frame1, 180)

        ret, self.frame2 = self.cam.read()
        contours, hirarchy = self._get_contours(self.frame1, self.frame2)
        is_mov = False
        # making rectangle around moving object
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            referenceArea = self._is_object(contour)
            if referenceArea is None:
                continue
            is_mov = True
            break
        self._process_mov(1, is_mov, ret, frame)
        return frame

    def get_frame_mov(self):
        if self.frame1 is None:
            _, self.frame1 = self.cam.read()
        elif self.frame2 is None:
            _, self.frame1 = self.cam.read()
        else:
            self.frame1 = self.frame2
        ret, self.frame2 = self.cam.read()
        contours, hirarchy = self._get_contours(self.frame1, self.frame2)
        is_mov = False
        # making rectangle around moving object
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            referenceArea = self._is_object(contour)
            if referenceArea is None:
                continue
            self._draw(self.frame1, x, y, w, h, "movimiento")
            is_mov = True
        self._process_mov(2, is_mov, ret, self.frame1)
        return self.frame1

    def _draw(self, frame, x, y, w, h, text):
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(frame, text, (x+5, y-5), self.font, 1, (255, 255, 255), 2)

    def _is_object(self, contour):
        referenceArea = cv2.contourArea(contour)
        if referenceArea < int(self.settings_camera["MIN_AREA_OBJECT"]):
            return None
        return referenceArea
    
    def _process_mov(self, type_cam, is_mov, ret, frame):
        item = { "type_cam": type_cam, "is_mov": is_mov, "ret": ret, "frame": frame }
        self._RECORD.put_nowait(item)
        if is_mov == True:
            if int(self.settings_camera["ON_GUARD"]) == 1:
                item = { "message" : "Se ha detectado un movimiento."}
                self._ALERT.put_nowait(item=item)
    
    def get_stream(self, type_cam = 1):
        if type_cam == 3:
            frame = self.get_frame_diff()
            ret, frame_jpeg = cv2.imencode('.jpg', frame)
            return frame_jpeg
        elif type_cam == 4:
            frame = self.get_frame_gray()
            ret, frame_jpeg = cv2.imencode('.jpg', frame)
            return frame_jpeg
        elif type_cam == 2:
            frame = self.get_frame_mov()
            ret, frame_jpeg = cv2.imencode('.jpg', frame)
            return frame_jpeg
        else:
            frame = self.get_frame_normal()
            ret, frame_jpeg = cv2.imencode('.jpg', frame)
            return frame_jpeg

    def generated_stream(self, type_cam = 1):
        self.initialize()
        while self.cam.isOpened():
            frame_jpeg = self.get_stream(type_cam=type_cam)
            if self.RELEASE_CAM == True or self.RELEASE_CAM is None:
                break
            else:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_jpeg.tobytes() + b'\r\n\r\n')

    def clear(self):
        try:
            self.frame1 = None
            self.frame2 = None
            if self.cam:
                self.cam.release()
        except Exception as e:
            print(e)

    def release(self, with_threading = False, window = False):
        try:
            self.RELEASE_CAM = True
            time.sleep(0.9)
            self.frame1 = None
            self.frame2 = None
            if self.cam:
                self.cam.release()
                if with_threading:
                    self.cam.stop()
            if window:
                cv2.destroyAllWindows()
            self._RECORD.release()
        except Exception as e:
            print(e)

    def __del__(self):
        try:
            self.RELEASE_CAM = None
            time.sleep(0.9)
            self.frame1 = None
            self.frame2 = None
            if self.cam:
                self.cam.release()
            self._RECORD.release()
            self._RECORD = None
            self._ALERT = None
            cv2.destroyAllWindows()
        except Exception as e:
            print(e)