from networktables import NetworkTables
from pipeline import ContourPipeline
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image as PImage
from datetime import datetime
from datetime import timedelta
import time
import numpy as np
import cv2
import sys
import math


##NetworkTables.initialize(server='10.2.79.2')
##print('Waiting to connect...')
##while NetworkTables.isConnected() == False:
##	time.sleep(0.1)
##
##nt = NetworkTables.getTable("Boiler")
imageWidth = 1640

def getDFromW(width):
	return 7362.30054*(math.pow(float(width),-1.186536))

def getDFromH(height):
	return 9963.977172*(math.pow(float(height),-1.072971))

def getDFromWt(widthTotal):
	return 5745.771277*(math.pow(float(widthTotal),-0.895025))

start_time = datetime.now()

def millis():
	dt = datetime.now() - start_time
	ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
	return ms

vis = ContourPipeline()
camera = PiCamera()
lastTime = -1
while True:
	currentMillis = lambda: int(round(time.time() * 1000))
	imgArray = PiRGBArray(camera, size=(1640, 1232))
	camera.resolution = (1640, 1232)
	camera.capture(imgArray, format="bgr", use_video_port=True)
	img = imgArray.array
	
	contours = vis.process(img)
	
	rectExists = False
	
	if 1 < len(contours):
		rect1 = cv2.boundingRect(contours[0])
		rect2 = cv2.boundingRect(contours[1])
		if rect1[1] > rect2[1]:
			topRect = rect1
			botRect = rect2
		else:
			topRect = rect2
			botRect = rect1
		
		cv2.rectangle(img, (topRect[0], ropRect[1]), (botRect[0]+botRect[2], botRect[1]+botRect[3]), (0,255,195), 2)
		cv2.imwrite('rectangle.png', img)
		
		rectExists = True
	else:
		rectExists = False
	
##	if(rectExists == True):
##		# declaring rectangle objects
##		class rectObj1:
##			# top left point
##			topLeftX = rect1[0]
##			pt1 = (rect1[0], rect1[1])
##			# bottom right point
##			bottomRightX = (rect1[0] + rect1[2])
##			pt2 = ((rect1[0] + rect1[2]), (rect1[1] + rect1[3]))
##			# width and height
##			w = rect1[2]
##			h = rect1[3]
##		if(rectObj1.pt1 < rectObj2.pt1):
##			leftRect = rectObj1
##			rightRect = rectObj2
##		else:
##			leftRect = rectObj2
##			rightRect = rectObj1
##
##		leftDist = getDFromW(leftRect.w)
##		rightDist = getDFromW(rightRect.w)
##		pixelOffset = (imageWidth/2)-((leftRect.topLeftX + rightRect.bottomRightX)/2)
##		lastTime = millis()
##		res1 = nt.putValue("distance", middleDist)
##		res2 = nt.putValue("eyes", True)
##		res3 = nt.putValue("lastTimeDetected", 0)
##		res4 = nt.putValue("pixelOffset", pixelOffset)
##	else:
##		if lastTime == -1:
##			timeSinceLast = -1
##		else:
##			timeSinceLast = millis() - lastTime
##		res2 = nt.putValue("eyes", False)
##		res3 = nt.putValue("lastTimeDetected", timeSinceLast)
