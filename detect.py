from vision import DetectColor
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np
import cv2
import sys

vis = DetectColor()
camera = PiCamera()
time.sleep(0.1)
imgArray = PiRGBArray(camera, size=(640, 480))
camera.capture(imgArray, format="bgr", resize=(640,480), use_video_port=True)

img = imgArray.array

processedImg = vis.process(img)
cv2.imwrite(sys.argv[1], vis.mask_output)

camera.close()
