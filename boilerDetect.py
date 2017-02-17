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

NetworkTables.initialize(server='10.2.79.2')
print('Waiting to connect...')
while NetworkTables.isConnected() == False:
	time.sleep(0.1)

nt = NetworkTables.getTable("Gear")
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

	rect1Exists = False
	rect2Exists = False
        rectangleScores = []
        for contour in contours:
            rect = cv2.boundingRect(contours[contour])
            class rectObj:
		# top left point
		topY = rect[1]
		leftX = rect[0]
		pt1 = (leftX, topY)
		# bottom right point
		botY = (rect[1]+rect[3])
		rightX = (rect[0] + rect[2])
		pt2 = (rightX, botY)
		# width and height
		w = rect1[2]
		h = rect1[3]
            ratio1 = cont
	if 0 < len(contours):
		rect1 = cv2.boundingRect(contours[0])
		rect1Exists = True
	else:
		rect1Exists = False

	if 1 < len(contours):
		rect2 = cv2.boundingRect(contours[1])
		rect2Exists = True
	else:
		rect2Exists = False

	if(rect1Exists == True):
		# declaring rectangle objects
		class rectObj1:
                        # top left point
                        topLeftX = rect1[0]
			pt1 = (rect1[0], rect1[1])
			# bottom right point
			bottomRightX = (rect1[0] + rect1[2])
			pt2 = ((rect1[0] + rect1[2]), (rect1[1] + rect1[3]))
			# width and height
			w = rect1[2]
			h = rect1[3]

	if(rect2Exists == True):
		class rectObj2:
			# top left point
			topLeftX = rect2[0]
			pt1 = (rect2[0], rect2[1])
			# bottom right point
			bottomRightX = (rect2[0] + rect2[2])
			pt2 = ((rect2[0] + rect2[2]), (rect2[1] + rect2[3]))
			# width and height
			w = rect2[2]
			h = rect2[3]

	if(rect1Exists == True) and (rect2Exists == True):
		if(rectObj1.pt1 < rectObj2.pt1):
			leftRect = rectObj1
			rightRect = rectObj2
		else:
			leftRect = rectObj2
			rightRect = rectObj1

		leftDist = getDFromW(leftRect.w)
		rightDist = getDFromW(rightRect.w)
		pixelOffset = (imageWidth/2)-((leftRect.topLeftX + rightRect.bottomRightX)/2)
		if(rightDist > leftDist):
			nearDist = leftDist
			farDist = rightDist
		elif(rightDist < leftDist):
			nearDist = rightDist
			farDist = leftDist
		else:
			middleDist = leftDist
			nearDist = middleDist
			farDist = middleDist

		if(nearDist != farDist):
			middleDist = (farDist + nearDist) / 2
			angle = 0
			try:
				angle = math.degrees(math.acos((26.2656+math.pow(middleDist,2)-math.pow(farDist,2))/(2*5.125*middleDist)))
			except:
				print("error")
			if leftDist < rightDist:
				angle *= -1
			lastTime = millis()
			res = nt.putValue("angle", angle)
			res1 = nt.putValue("distance", middleDist)
			res2 = nt.putValue("eyes", True)
			res3 = nt.putValue("lastTimeDetected", 0)
			res4 = nt.putValue("pixelOffset", pixelOffset)
		else:
			lastTime = millis()
			res = nt.putValue("angle", 0)
			res1 = nt.putValue("distance", middleDist)
			res2 = nt.putValue("eyes", True)
			res3 = nt.putValue("lastTimeDetected", 0)
			res4 = nt.putValue("pixelOffset", pixelOffset)
	else:
		if lastTime == -1:
			timeSinceLast = -1
		else:
			timeSinceLast = millis() - lastTime
		res2 = nt.putValue("eyes", False)
		res3 = nt.putValue("lastTimeDetected", timeSinceLast)
