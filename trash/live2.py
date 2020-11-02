#!/usr/bin/python3.8
#OpenCV 4.2, Raspberry pi 3/3b/4b
import cv2
import numpy as np

def get_detector_with_params_circle():
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

def _process_circle(detector, frame):
    # Detect blobs.
    keypoints = detector.detect(frame)
    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(frame, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return im_with_keypoints

def _show(name, item):
    # Show keypoints circle
    cv2.imshow(name, item)

def _process_frame(frame1, frame2):
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
    return contours, hirarchy, thresh

def _draw_rectangle(frame, x, y, w, h, text):
    cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 255), 2)
    cv2.putText(frame, text, (x+5, y-5), font, 1, (255, 255, 255), 2)

def _is_object(contour):
    referenceArea = cv2.contourArea(contour)
    if referenceArea < 10000:
        return None
    return referenceArea


# capturing video
cap = cv2.VideoCapture(0)
# cap.set(3, 640) # set video width
# cap.set(4, 480) # set video height
# reading back-to-back frames(images) from video
cont = 0
font = cv2.FONT_HERSHEY_SIMPLEX
REFERENCE_AREA = 36

detector = get_detector_with_params_circle()

ret, frame1 = cap.read()
ret, frame2 = cap.read()

while cap.isOpened():
    contours, hirarchy, thresh = _process_frame(frame1, frame2)
    # making rectangle around moving object
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        referenceArea = _is_object(contour)
        if referenceArea is None:
            continue
        text = "area {} px2".format(referenceArea)
        _draw_rectangle(frame1, x, y, w, h, text)
        #im_with_keypoints = _process_circle(detector, frame2)
        print("hay movimiento", cont)
        cont += 1
    
    #_show("circle", im_with_keypoints)
    # Display original frame
    _show('Motion Detector', frame1)
    # Display Diffrenciate Frame - escala gris - muestra los cambios
    #_show('Difference Frame', thresh)
    # Displaying image in gray_scale
    # cv2.imshow("Gray_Frame", gray)
    # Assign frame2(image) to frame1(image)
    frame1 = frame2
    # Read new frame2
    ret, frame2 = cap.read()
    # Press 'esc' for quit
    if cv2.waitKey(40) == 27:
        break

# Release cap resource
cap.release()
# Destroy all windows
cv2.destroyAllWindows()
