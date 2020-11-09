#!/usr/bin/python3.8
#OpenCV 4.2, Raspberry pi 3/3b/4b - test on macOS
import cv2
import numpy as np
#import threading
import time
from utils.dir import get_data_xml

class Camera:#(threading.Thread):
    #lock = threading.Lock()
    def __init__(self, cam_id = 0, on_guard = False, show_gray_cam = False, show_difference_cam = False, capture_face = False):
        super().__init__()
        #threading.Thread.__init__(self)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.show_difference_cam = show_difference_cam
        self.show_gray_cam = show_gray_cam
        self.capture_face = capture_face
        self.on_guard = on_guard
        #cam and dimentions
        self.cam_id = cam_id
        self.cam = None
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.fps = 20
        self.out = None
        self.frame1 = None
        self.frame2 = None
        self.RELEASE_CAM = False
        # set classifier
        self._put_classifier()

    #initialize
    def initialize(self):
        self.RELEASE_CAM = False
        if self.cam and self.cam.isOpened():
            return
        elif self.cam:
            self.clear()
        self._put_cam_video()

    def _put_classifier(self):
        path = get_data_xml('haarcascade_frontalface_default.xml')
        self.faceCascade = cv2.CascadeClassifier(path)

    def _put_cam_video(self):
        self.cam = cv2.VideoCapture(self.cam_id)
        fheight = int(self.cam.get(3))
        fwidth = int(self.cam.get(4))
        self.cam.set(3,fheight)
        self.cam.set(4,fwidth)
        self.out = cv2.VideoWriter('output.avi', self.fourcc, self.fps, (fheight, fwidth))

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
            self._draw(self.frame1, x, y, w, h, "objeto")
            if self.capture_face == True:
                self._process_face(self.frame1)
            is_mov = True
        return self.frame1

    def _draw(self, frame, x, y, w, h, text):
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(frame, text, (x+5, y-5), self.font, 1, (255, 255, 255), 2)

    def _is_object(self, contour):
        referenceArea = cv2.contourArea(contour)
        if referenceArea < 10000:
            return None
        return referenceArea
    
    def _show(self, name, item):
        cv2.namedWindow(name)        # Create a named window
        cv2.moveWindow(name, 40, 30)  # Move it to (40,30)
        cv2.imshow(name, item)
    
    def _process_mov(self, ret, frame):
        self._record(ret, frame)
        if self.on_guard == True:
            print("hay movimiento")

    def _process_face(self, frame):
        if self.faceCascade:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,      
                minSize=(100, 100)
            )
            for (x,y,w,h) in faces:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

    def _record(self, ret, frame):
        if ret and ret == True:
            self.out.write(frame)
    
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
    
    def capture(self):
        if self.cam and self.cam.isOpened():
            return
        else:
            self.initialize()

    def generated_stream(self, type_cam = 1):
        self.capture()
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
            if self.out:
                self.out.release()
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
            if self.out:
                self.out.release()
            if window:
                cv2.destroyAllWindows()
        except Exception as e:
            print(e)

    def __del__(self):
        try:
            print("saliendo")
            self.RELEASE_CAM = None
            time.sleep(0.9)
            self.frame1 = None
            self.frame2 = None
            if self.cam:
                self.cam.release()
            if self.out:
                self.out.release()
            cv2.destroyAllWindows()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    a = Camera()
    a.capture()
    while a.cam.isOpened():
        frame = a.generated_stream()
        a._show('Frame', frame)
        if cv2.waitKey(40) == 27:
            break
    a.release(window=True)