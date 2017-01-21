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
img = cv2.imread('image1.png')
contours = vis.process(img)
rect1 = cv2.boundingRect(contours[0])
rect2 = cv2.boundingRect(contours[1])
print(str(rect1))
print(str(rect2))
color = (100,0,255)
point11 = (rect1[0], rect1[1])
print(str(point11))
point21 = ((rect1[0] + rect1[2]), (rect1[1] + rect1[3]))
print(str(point21))
img = cv2.rectangle(img, point11, point21, color, thickness=2, lineType=8, shift=0)
point12 = (rect2[0], rect2[1])
print(str(point12))
point22 = ((rect2[0] + rect2[2]), (rect2[1] + rect2[3]))
img = cv2.rectangle(img, point12, point22, color, thickness=2, lineType=8, shift=0)

cv2.imwrite('output.png', img)

# camera.close()
