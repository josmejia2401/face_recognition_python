#!/usr/bin/env python3
#!/usr/bin/python3.8
# OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
import cv2
import time
import copy
from dto.record import ConfigDTO

class Frame:

    def __init__(self, config: ConfigDTO = None):
        super().__init__()
        self.__config = copy.deepcopy(config)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
    
    #320x240, 640x480, 800x480, 1024x600, 1024x768, 1440x900, 1920x1200, 1280x720, 1920x1080, 768x576, 720x480
    def resize(self, frame) -> any:
        if frame is None:
            return False, None
        frame = cv2.resize(frame, (self.__config.camera.dimWidth, self.__config.camera.dimHeight))
        return frame

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
        grabbed, thresh = self.__get_frame_diff(frame1, frame2)
        return True, thresh

    def get_frame_normal(self, frame1, frame2):
        #frame = cv2.flip(frame1, 180)
        return True, frame1

    def get_frame_mov(self, frame1, frame2):
        contours, _ = self.__get_contours(frame1, frame2)
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            referenceArea = self.__is_object(contour)
            if referenceArea is None:
                continue
            self.__draw(frame1, x, y, w, h, "movimiento")
        return True, frame1
    
    def is_movement(self, frame1, frame2):
        contours, _ = self.__get_contours(frame1, frame2)
        is_mov = False
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            referenceArea = self.__is_object(contour)
            if referenceArea is None:
                continue
            is_mov = True
            break
        return is_mov

    def __draw(self, frame, x, y, w, h, text):
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(frame, text, (x+5, y-5), self.font, 1, (255, 255, 255), 2)

    def __is_object(self, contour):
        referenceArea = cv2.contourArea(contour)
        if referenceArea < self.__config.general.minAreaObject:
            return None
        return referenceArea

    def frame_to_image(self, frame) -> any:
        if frame is None:
            return False, None
        ret, jpeg = cv2.imencode('.jpg', frame)
        return ret, jpeg
    
    