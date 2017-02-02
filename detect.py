from pipeline import ContourPipeline
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np
import cv2
import sys
import math

vis = ContourPipeline()
# camera = PiCamera()
time.sleep(0.1)
imageHeight = 480
fovH = 48.8
# imgArray = PiRGBArray(camera, size=(640, 360))
# camera.capture(imgArray, format="bgr", resize=(640,360), use_video_port=True)

# img = imgArray.array
img = cv2.imread('test1.png')
contours = vis.process(img)

rect1Exists = False
rect2Exists = False

if 0 < len(contours):
    rect1 = cv2.boundingRect(contours[0])
    print(str(rect1))
    rect1Exists = True
else:
    print('contour 1 not found')
    rect1Exists = False

if 1 < len(contours):
    rect2 = cv2.boundingRect(contours[1])
    print(str(rect2))
    rect2Exists = True
else:
    print('contour 2 not found')
    rect2Exists = False

# declaring pink color for drawing bounding rectangle
color = (100,0,255)

# Check if the first contour was found
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
    
    print(str(rectObj1.w))
    print(str(rectObj1.h))
    img = cv2.rectangle(img, rectObj1.pt1, rectObj1.pt2, color, thickness=2, lineType=8, shift=0)

# Check if a second contour was found
if(rect2Exists == True):    
    class rectObj2:
        # top left point
        pt1 = (rect2[0], rect2[1])
        # bottom right point
        pt2 = ((rect2[0] + rect2[2]), (rect2[1] + rect2[3]))
        # width and height
        w = rect2[2]
        h = rect2[3]
    print(str(rectObj2.w))
    print(str(rectObj2.h))
    img = cv2.rectangle(img, rectObj2.pt1, rectObj2.pt2, color, thickness=2, lineType=8, shift=0)

cv2.imwrite('output.png', img)

if(rect1Exists == True) and (rect2Exists == True):
    
    if(rectObj1.pt1 < rectObj2.pt1):
        leftRect = rectObj1
        rightRect = rectObj2
    else:
        leftRect = rectObj2
        rightRect = rectObj1
    
    leftRatio = leftRect.h / imageHeight
    leftFocDist = 5 / leftRatio
    leftOpposite = leftFocDist / 2
    leftDist = leftOpposite / math.tan(math.radians(fovH / 2))

    rightRatio = rightRect.h / imageHeight
    rightFocDist = 5 / rightRatio
    rightOpposite = rightFocDist / 2
    rightDist = rightOpposite / math.tan(math.radians(fovH / 2))

    if(rightDist > leftDist):
        nearDist = leftDist
        farDist = rightDist
        print("nearDist: " + str(nearDist))
        print("farDist: " + str(farDist))
    elif(rightDist < leftDist):
        nearDist = rightDist
        farDist = leftDist
        print("nearDist: " + str(nearDist))
        print("farDist: " + str(farDist))
    else:
        middleDist = leftDist
        nearDist = middleDist
        farDist = middleDist
    
    
    if(nearDist != farDist):
        middleDist = (farDist + nearDist) / 2
        print("middleDist: " + str(middleDist))
        angle = math.degrees(math.acos(nearDist / middleDist))
    else:
        angle = 0
    

    print(str(middleDist))
    print(str(angle))
else:
    print("target not in sight")


# camera.close()
