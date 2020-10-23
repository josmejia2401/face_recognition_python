#!/usr/bin/python3.8
#OpenCV 4.2, Raspberry pi 3/3b/4b
import cv2
import numpy as np
import threading

#from utils.dir import get_data_xml
from pathlib import Path
import os
current_path = Path(__file__)

def get_data_xml(name):
    c_path = current_path
    x_path = os.path.join(str(c_path), 'data', 'xml')
    my_file = Path(x_path)
    con = 0
    while my_file.exists() == False:
        if con > 3:
            break
        c_path = c_path.parent
        x_path = os.path.join(str(c_path), 'data', 'xml')
        my_file = Path(x_path)
        con += 1
    
    my_file = os.path.join(str(my_file), name)
    my_file = Path(my_file)
    if my_file.exists() == False:
        raise Exception("not found")
    return str(my_file)

class Camera:#(threading.Thread):

    #lock = threading.Lock()

    def __init__(self, cam_sel = 0, on_guard = False, show_gray_cam = False, show_difference_cam = False, capture_face = False):
        #super().__init__()
        #threading.Thread.__init__(self)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.show_difference_cam = show_difference_cam
        self.show_gray_cam = show_gray_cam
        self.capture_face = capture_face
        self.on_guard = on_guard
        #cam and dimentions
        self.cam_sel = cam_sel
        self.cam = None
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.fps = 20
        self.out = None
        self.frame1 = None
        self.frame2 = None
        self.frame_prev = None
    
    def override_params(self, on_guard = False, show_gray_cam = False, show_difference_cam = False, capture_face = False):
        self.show_difference_cam = show_difference_cam
        self.show_gray_cam = show_gray_cam
        self.capture_face = capture_face
        self.on_guard = on_guard

    def _put_cam_video(self):
        if self.cam and self.cam.isOpened():
            # Release cap resource
            self.cam.release()
            # Destroy all windows
            cv2.destroyAllWindows()
        
        if self.out:
            self.out.release()

        self.cam = cv2.VideoCapture(self.cam_sel)
        fheight = int(self.cam.get(3))
        fwidth = int(self.cam.get(4))
        self.cam.set(3,fheight)
        self.cam.set(4,fwidth)
        self.out = cv2.VideoWriter('output.avi', self.fourcc, self.fps, (fheight, fwidth))

    def _process_frame(self, frame1, frame2):
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
        return contours, hirarchy, thresh, gray

    def _draw(self, frame, x, y, w, h, text):
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(frame, text, (x+5, y-5), self.font, 1, (255, 255, 255), 2)
        if self.capture_face == True:
            self._process_face(frame)

    def _is_object(self, contour):
        referenceArea = cv2.contourArea(contour)
        if referenceArea < 10000:
            return None
        return referenceArea
    
    def _show(self, name, item):
        # Show keypoints circle
        cv2.namedWindow(name)        # Create a named window
        cv2.moveWindow(name, 40, 30)  # Move it to (40,30)
        cv2.imshow(name, item)
    
    def _call_notification(self):
        if self.on_guard == True:
            print("hay movimiento")

    def _put_classifier(self):

        path = get_data_xml('haarcascade_frontalface_default.xml')
        self.faceCascade = cv2.CascadeClassifier(path)

        #path = get_data_xml('haarcascade_eye.xml')
        #self.eyeCascade = cv2.CascadeClassifier(path)

        #path = get_data_xml('haarcascade_smile.xml')
        #self.smileCascade = cv2.CascadeClassifier(path)

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
                #roi_gray = gray[y:y+h, x:x+w]
                #roi_color = frame[y:y+h, x:x+w]
                #eyes = self.eyeCascade.detectMultiScale(
                #    roi_gray,
                #    scaleFactor= 1.5,
                #    minNeighbors=5,
                #    minSize=(5, 5),
                #    )
                #for (ex, ey, ew, eh) in eyes:
                #    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    def _record(self, ret, frame):
        if ret and ret == True:
            # write the flipped frame
            self.out.write(frame)

    def _process_mov(self, ret, frame):
        self._record(ret, frame)
        self._call_notification()

    def get_cam(self):
        return self.cam

    def _check_frames(self):
        if self.frame1 and self.frame2:
            return
        self.ret, self.frame1 = self.cam.read()
        self.ret, self.frame2 = self.cam.read()
        return
    
    def get_frame_all(self):
        frame_original = cv2.flip(self.frame1, 180)
        contours, hirarchy, frame_diff, frame_gray = self._process_frame(self.frame1, self.frame2)
        is_mov = False
        # making rectangle around moving object
        for contour in contours:
            #
            (x, y, w, h) = cv2.boundingRect(contour)
            referenceArea = self._is_object(contour)
            #
            if referenceArea is None:
                continue
            #
            text = "area {} px2".format(referenceArea)
            self._draw(self.frame1, x, y, w, h, text)
            #
            is_mov = True
        frame_mov = self.frame1
        ret, frame_jpeg = cv2.imencode('.jpg', frame_original)
        #
        self.frame1 = self.frame2
        # Read new frame2
        self.ret, self.frame2 = self.cam.read()
        return frame_diff, frame_gray, frame_mov, frame_original, frame_jpeg, self.ret, is_mov

    def get_frame_streaming_normal(self):
        ret, frame_original = self.cam.read()
        frame_original = cv2.flip(frame_original, 180)
        ret, frame_jpeg = cv2.imencode('.jpg', frame_original)
        return ret, frame_jpeg
    
    def get_frame_streaming_mov(self):
        if not self.frame_prev:
            self.ret_prev, self.frame_prev = self.cam.read()
        self.ret_current, self.frame_current = self.cam.read()

        frame_original = cv2.flip(self.frame_current, 180)
        contours, hirarchy, frame_diff, frame_gray = self._process_frame(self.frame_prev, self.frame_current)
        is_mov = False
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            referenceArea = self._is_object(contour)
            if referenceArea is None:
                continue
            text = "area {} px2".format(referenceArea)
            self._draw(self.frame_prev, x, y, w, h, text)
            is_mov = True
        
        if is_mov:
            ret, frame_jpeg = cv2.imencode('.jpg', self.frame_prev)
        else:
            ret, frame_jpeg = cv2.imencode('.jpg', self.frame_current)

        self.frame_prev = self.frame_current
        self.ret, self.frame_current = self.cam.read()
        return ret, frame_jpeg, is_mov

    def release(self):
        try:
            # Release cap resource
            self.cam.release()
            # Destroy all windows
            cv2.destroyAllWindows()
            self.out.release()
        except Exception as e:
            print(e)

    def initialize(self):
        self._put_classifier()
        self._put_cam_video()
        self._check_frames()

if __name__ == "__main__":
    a = Camera()
    a.initialize()
    cam = a.get_cam()
    while cam.isOpened():
        frame_diff, frame_gray, frame_mov, frame_original, frame_jpeg, ret, is_mov = a.get_frame_all()
        a._show('Normal Frame', frame_mov)

        if is_mov == True:
            a._process_mov(ret, frame_original)

        if cv2.waitKey(40) == 27:
            break
    a.release()