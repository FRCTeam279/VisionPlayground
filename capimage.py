from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np
import cv2
import sys



camera = PiCamera()
time.sleep(0.1)
imgArray = PiRGBArray(camera, size=(1640, 1232))
camera.capture(imgArray, format="bgr", resize=(1640, 1232), use_video_port=True)

img = imgArray.array

print(sys.argv)
cv2.imwrite(sys.argv[1], img)

camera.close()
