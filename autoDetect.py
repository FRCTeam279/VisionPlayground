from networktables import NetworkTables
from pipeline import ContourPipeline
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image as PImage
from PIL import ImageTk
import tkinter
from tkinter import *
import imutils
import time
import numpy as np
import cv2
import sys
import math

NetworkTables.initialize(server='10.2.79.2')
print('Waiting to connect...')
while NetworkTables.isConnected() == False:
    time.sleep(0.1)

nt = NetworkTables.getTable("BLAHBLAHBLAH")
imageHeight = 1232

def getDFromW(width):
    return 7362.30054*(width^-1.186536)

def getDFromH(height):
    return 9963.977172*(height^-1.072971)

def getDFromWt(widthTotal):
    return 5745.771277*(widthTotal^-0.895025)

vis = ContourPipeline()

imgArray = PiRGBArray(self.camera, size=(1640, 1232))
camera.resolution = (1640, 1232)
camera.capture(imgArray, format="bgr", use_video_port=True)
img = imgArray.array

contours = vis.process(img)

rect1Exists = False
rect2Exists = False

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
        pt1 = (rect1[0], rect1[1])
        # bottom right point
        pt2 = ((rect1[0] + rect1[2]), (rect1[1] + rect1[3]))
        # width and height
        w = rect1[2]
        h = rect1[3]

if(rect2Exists == True):    
    class rectObj2:
        # top left point
        pt1 = (rect2[0], rect2[1])
        # bottom right point
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
            
            leftDist = getDfromW(leftRect.w)
            rightDist = getDfromW(rightRect.w)
            
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
                angle = math.degrees(math.acos((26.2656+(middleDist^2)-(farDist^2))/(2*5.125*middleDist))
                if(leftDist < rightDist):
                    angle *= -1
                res = nt.putValue("angle", angle)
                res1 = nt.putValue("distance", middleDist)
                res2 = nt.putValue("eyes", True)
            else:
                res = nt.putValue("angle", 0)
                res1 = nt.putValue("distance", middleDist)
                res2 = nt.putValue("eyes", True)
        else:
            res = nt.putValue("angle", -999)
            res1 = nt.putValue("distance", -999)
            res2 = nt.putValue("eyes", False)
