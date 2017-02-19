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
while NetworkTables.isConnected() is False:
    time.sleep(0.1)

nt = NetworkTables.getTable("Gear")
imageWidth = 1640


def getDFromW(width):
    return 7362.30054*(math.pow(float(width), -1.186536))


def getDFromH(height):
    return 9963.977172*(math.pow(float(height), -1.072971))


def getDFromWt(widthTotal):
    return 5745.771277*(math.pow(float(widthTotal), -0.895025))


start_time = datetime.now()


def millis():
    dt = datetime.now() - start_time
    ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
    return ms


vis = ContourPipeline()
camera = PiCamera()
lastTime = -1
frameCount = 0
lastFramePeriodTime = millis()
while True:
    frameCount += 1
    if frameCount == 10:
        frameCount = 0
        currentPeriodSeconds = (millis() - lastFramePeriodTime) / 1000
        framesPerSecond = 10 / currentPeriodSeconds
        lastFramePeriodTime = millis()
        nt.putValue("fps", framesPerSecond)
    imgArray = PiRGBArray(camera, size=(1640, 1232))
    camera.resolution = (1640, 1232)
    camera.capture(imgArray, format="bgr", use_video_port=True)
    img = imgArray.array
    contours = vis.process(img)
    if 1 < len(contours):
        rect1 = cv2.boundingRect(contours[0])
        rect2 = cv2.boundingRect(contours[1])
        if rect1[0] < rect2[0]:
            class leftRect:
                # top left point
                topLeftX = rect1[0]
                pt1 = (rect1[0], rect1[1])
                # bottom right point
                bottomRightX = (rect1[0] + rect1[2])
                pt2 = ((rect1[0] + rect1[2]), (rect1[1] + rect1[3]))
                # width and height
                w = rect1[2]
                h = rect1[3]

            class rightRect:
                # top left point
                topLeftX = rect2[0]
                pt1 = (rect2[0], rect2[1])
                # bottom right point
                bottomRightX = (rect2[0] + rect2[2])
                pt2 = ((rect2[0] + rect2[2]), (rect2[1] + rect2[3]))
                # width and height
                w = rect2[2]
                h = rect2[3]
        else:
            class leftRect:
                # top left point
                topLeftX = rect1[0]
                pt1 = (rect1[0], rect1[1])
                # bottom right point
                topRightX = (rect1[0] + rect1[2])
                pt2 = ((rect1[0] + rect1[2]), (rect1[1] + rect1[3]))
                # width and height
                w = rect1[2]
                h = rect1[3]

            class rightRect:
                # top left point
                topLeftX = rect2[0]
                pt1 = (rect2[0], rect2[1])
                # bottom right point
                topRightX = (rect2[0] + rect2[2])
                pt2 = ((rect2[0] + rect2[2]), (rect2[1] + rect2[3]))
                # width and height
                w = rect2[2]
                h = rect2[3]
        leftDist = getDFromW(leftRect.w)
        rightDist = getDFromW(rightRect.w)
        # time.sleep(3)
        pixelOffset = (imageWidth/2)-((leftRect.topLeftX + rightRect.topRightX)/2)
        inchOffset = pixelOffset / (((leftRect.w + rightRect.w)/2) / 5)
        # cv2.rectangle(img, leftRect.pt1, leftRect.pt2, (0, 255, 0), 2)
        # cv2.rectangle(img, rightRect.pt1, rightRect.pt2, (0, 255, 0), 2)
        # cv2.imwrite('output.png', img)
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
            except ValueError:
                print("Math domain error")
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
