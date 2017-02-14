from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np
import cv2
import sys



camera = PiCamera()
time.sleep(0.1)
#imgArray = PiRGBArray(camera, size=(640, 480))
#camera.capture(imgArray, format="bgr", resize=(640, 480), use_video_port=True)
imgArray = PiRGBArray(camera, size=(640, 480))
camera.capture(imgArray, format="bgr", resize=(640, 480), use_video_port=True)

img = imgArray.array

#print(sys.argv)
cv2.imshow('picture', img)
cv2.imwrite(sys.argv[1], img)

camera.close()
