from pipeline import ContourPipeline
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np
import cv2
import sys

vis = ContourPipeline()
# camera = PiCamera()
time.sleep(0.1)
# imgArray = PiRGBArray(camera, size=(640, 360))
# camera.capture(imgArray, format="bgr", resize=(640,360), use_video_port=True)

# img = imgArray.array
img = cv2.imread('image6.png')
contours = vis.process(img)

rect1Exists = False
rect2Exists = False

if 0 < len(contours):
    rect1 = cv2.boundingRect(contours[0])
    print(str(rect1))
    rect1Exists = True
else:
    print('contour not found')
    rect1Exists = False

if 1 < len(contours):
    rect2 = cv2.boundingRect(contours[1])
    print(str(rect2))
    rect2Exists = True
else:
    print('contour not found')
    rect2Exists = False

# declaring pink color for drawing bounding rectangle
color = (100,0,255)
if(rect1Exists == True):
    # declaring rectangle objects
    class rectObj1:
        # top left point
        pt1 = (rect1[0], rect1[1])
        # bottom right point
        pt2 = ((rect1[0] + rect1[2]), (rect1[1] + rect1[3]))
        # width and height
        w = rect1[2]
        h = rect1[3]
    
    print(str(rectObj1.pt1))
    print(str(rectObj1.pt2))
    img = cv2.rectangle(img, rectObj1.pt1, rectObj1.pt2, color, thickness=2, lineType=8, shift=0)

if(rect2Exists == True):    
    class rectObj2:
        # top left point
        pt1 = (rect2[0], rect2[1])
        # bottom right point
        pt2 = ((rect2[0] + rect2[2]), (rect2[1] + rect2[3]))
        # width and height
        w = rect1[2]
        h = rect1[3]
    print(str(rectObj2.pt1))
    print(str(rectObj2.pt2))
    img = cv2.rectangle(img, rectObj2.pt1, rectObj2.pt2, color, thickness=2, lineType=8, shift=0)

cv2.imwrite('output.png', img)

if(rect1Exists == True) and (rect2Exists == True):
    
    if(rectObj1.pt1 < rectObj2.pt1):
        leftRect = rectObj1
        rightRect = rectObj2
    else:
        leftRect = rectObj2
        rightRect = rectObj1



# camera.close()
