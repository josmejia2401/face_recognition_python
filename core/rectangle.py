#!/usr/bin/python3.8
#OpenCV 4.2, Raspberry pi 3/3b/4b
import cv2
import numpy as np
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

class Rectangle:

    def __init__(self, show_gray_cam = False, show_difference_cam = False):
        super().__init__()
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.show_difference_cam = show_difference_cam
        self.show_gray_cam = show_gray_cam
        self.cam = None

    def _put_cam_video(self):
        if self.cam and self.cam.isOpened():
            # Release cap resource
            self.cam.release()
            # Destroy all windows
            cv2.destroyAllWindows()
        
        self.cam = cv2.VideoCapture(0)
        #self.cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        fheight = int(self.cam.get(3))
        fwidth = int(self.cam.get(3))
        self.cam.set(3,fheight)
        self.cam.set(4,fwidth)
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.fps = 20
        self.out = cv2.VideoWriter('output.avi', self.fourcc, self.fps, (int(self.cam.get(3)), int(self.cam.get(4))))

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
        self._process_face(frame)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(frame, text, (x+5, y-5), self.font, 1, (255, 255, 255), 2)

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
        print("hay movimiento")
    

    def _put_classifier(self):
        path = get_data_xml('haarcascade_frontalface_default.xml')
        self.faceCascade = cv2.CascadeClassifier(path)

        path = get_data_xml('haarcascade_eye.xml')
        self.eyeCascade = cv2.CascadeClassifier(path)

        path = get_data_xml('haarcascade_smile.xml')
        self.smileCascade = cv2.CascadeClassifier(path)

    def _process_face(self, frame):
        if self.faceCascade and self.eyeCascade:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,      
                minSize=(100, 100)
            )
            for (x,y,w,h) in faces:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                #ojos
                eyes = self.eyeCascade.detectMultiScale(
                    roi_gray,
                    scaleFactor= 1.5,
                    minNeighbors=5,
                    minSize=(5, 5),
                    )
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    def process(self):
        self._put_classifier()
        self._put_cam_video()

        ret, frame1 = self.cam.read()
        ret, frame2 = self.cam.read()
        while self.cam.isOpened():
            try:
                frame1 = cv2.flip(frame1, 180) # movñimiento de la camara igual q en real, si voy a izquierda se pinta izquierda
                contours, hirarchy, thresh, gray = self._process_frame(frame1, frame2)
                # making rectangle around moving object
                for contour in contours:
                    (x, y, w, h) = cv2.boundingRect(contour)
                    referenceArea = self._is_object(contour)
                    if referenceArea is None:
                        continue
                    text = "area {} px2".format(referenceArea)
                    self._draw(frame1, x, y, w, h, text)
                    self._call_notification()

                    if ret and ret == True:
                        # write the flipped frame
                        self.out.write(frame1)
                #normal
                self._show('Normal Frame', frame1)

                if self.show_difference_cam == True:
                    self._show('Difference Frame', thresh)

                if self.show_gray_cam == True:
                    self._show("Gray Frame", gray)

                # Assign frame2(image) to frame1(image)
                frame1 = frame2
                # Read new frame2
                ret, frame2 = self.cam.read()
                if cv2.waitKey(40) == 27:
                    break
            except Exception as e:
                print(e)
        
        try:
            # Release cap resource
            self.cam.release()
            # Destroy all windows
            cv2.destroyAllWindows()
            self.out.release()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    a = Rectangle()
    a.process()