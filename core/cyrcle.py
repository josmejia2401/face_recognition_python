#!/usr/bin/python3.8
#OpenCV 4.2, Raspberry pi 3/3b/4b
import cv2
import numpy as np

class Cyrcle:
    def __init__(self):
        super().__init__()
    
    def get_detector_with_params_circle(self):
        # Setup SimpleBlobDetector parameters.
        params = cv2.SimpleBlobDetector_Params()
        # Change thresholds
        params.minThreshold = 0
        params.maxThreshold = 255
        # Set edge gradient
        params.thresholdStep = 5
        # Filter by Area.
        params.filterByArea = True
        params.minArea = 1000
        # Set up the detector with default parameters.
        detector = cv2.SimpleBlobDetector_create(params)
        return detector

    def _process_circle(self, detector, frame):
        # Detect blobs.
        keypoints = detector.detect(frame)
        # Draw detected blobs as red circles.
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
        im_with_keypoints = cv2.drawKeypoints(frame, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        return im_with_keypoints
