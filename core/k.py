#!/usr/bin/python3.8
#OpenCV 4.2, Raspberry pi 3/3b/4b
import cv2
import numpy as np

class K:
    def __init__(self):
        super().__init__()
    
    def _set_cam_video(self):
        # capturing video
        self.cam = cv2.VideoCapture(0)
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def _show(self, name, item):
        # Show keypoints circle
        cv2.imshow(name, item)