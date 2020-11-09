#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
import cv2
import time
from utils.settings import get_settings_camera

class Frame:

    def __init__(self):
        super().__init__()
        self.SETTINGS = get_settings_camera()
        self.font = cv2.FONT_HERSHEY_SIMPLEX
    
    def __get_frame_diff(self, frame1, frame2):
        # Difference between frame1(image) and frame2(image)
        diff = cv2.absdiff(frame1, frame2)
        # Converting color image to gray_scale image
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        # Converting gray scale image to GaussianBlur, so that change can be find easily
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # If pixel value is greater than 20, it is assigned white(255) otherwise black
        grabbed, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        return grabbed, thresh

    def __get_contours(self, frame1, frame2):
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

    def get_frame_diff(self, frame1, frame2):
        contours, hirarchy = self.__get_contours(frame1, frame2)
        is_mov = False
        # making rectangle around moving object
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            referenceArea = self.__is_object(contour)
            if referenceArea is None:
                continue
            is_mov = True
            break
        grabbed, thresh = self.__get_frame_diff(frame1, frame2)
        return grabbed, thresh, is_mov

    def get_frame_normal(self, frame1, frame2):
        frame = cv2.flip(frame1, 180)
        contours, hirarchy = self.__get_contours(frame1, frame2)
        is_mov = False
        # making rectangle around moving object
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            referenceArea = self.__is_object(contour)
            if referenceArea is None:
                continue
            is_mov = True
            break
        return True, frame, is_mov

    def get_frame_mov(self, frame1, frame2):
        contours, hirarchy = self.__get_contours(frame1, frame2)
        is_mov = False
        # making rectangle around moving object
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            referenceArea = self.__is_object(contour)
            if referenceArea is None:
                continue
            self.__draw(frame1, x, y, w, h, "movimiento")
            is_mov = True
        return True, frame1, is_mov

    def __draw(self, frame, x, y, w, h, text):
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(frame, text, (x+5, y-5), self.font, 1, (255, 255, 255), 2)

    def __is_object(self, contour):
        referenceArea = cv2.contourArea(contour)
        if referenceArea < int(self.SETTINGS["MIN_AREA_OBJECT"]):
            return None
        return referenceArea
    #320x240, 640x480, 800x480, 1024x600, 1024x768, 1440x900, 1920x1200, 1280x720, 1920x1080, 768x576, 720x480
    def get_stream_to_image(self, frame, width = 640, heigth = 480) -> any:
        if frame is None:
            return False, None
        frame = cv2.resize(frame, (width, heigth))
        ret, jpeg = cv2.imencode('.jpg', frame)
        return ret, jpeg
    
    