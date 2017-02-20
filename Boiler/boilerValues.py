from networktables import NetworkTables
from pipeline import ContourPipeline
from picamera.array import PiRGBArray
from picamera import PiCamera
from datetime import datetime
import time
import cv2
import math

NetworkTables.initialize(server='10.2.79.2')
print('Waiting to connect...')
while NetworkTables.isConnected() is False:
    time.sleep(0.1)

nt = NetworkTables.getTable("Gear")
# imageWidth = 1280


# def getDFromW(width):
#     return 7362.30054*(math.pow(float(width), -1.186536))


# def getDFromH(height):
#     return 9963.977172*(math.pow(float(height), -1.072971))


# def getDFromWt(widthTotal):
#     return 5745.771277*(math.pow(float(widthTotal), -0.895025))


start_time = datetime.now()


# def millis():
#     dt = datetime.now() - start_time
#     ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
#     return ms


vis = ContourPipeline()
camera = PiCamera()
while True:
    imgArray = PiRGBArray(camera, size=(1280, 720))
    camera.resolution = (1280, 720)
    camera.capture(imgArray, format="bgr", use_video_port=True)
    img = imgArray.array
    contours = vis.process(img)
    # Checking if 2 contours exist
    if 1 < len(contours):
        # Creating bounding rectangles around each contour
        rect1 = cv2.boundingRect(contours[0])
        rect2 = cv2.boundingRect(contours[1])
        # creating class object to hold values for first contour

        class rectObj1:
            topY = rect1[1]
            botY = (rect1[1] - rect1[3])
            leftX = rect1[0]
            rightX = rect1[0] + rect1[2]
            # top left point
            pt1 = (leftX, topY)
            # bottom right point
            pt2 = (rightX, botY)
            # width and height
            w = rect1[2]
            h = rect1[3]
        # creating class object to hold values for second contour

        class rectObj2:
            topY = rect2[1]
            botY = (rect2[1] - rect2[3])
            leftX = rect2[0]
            rightX = rect2[0] + rect2[2]
            # top left point
            pt1 = (leftX, topY)
            # bottom right point
            pt2 = (rightX, botY)
            # width and height
            w = rect2[2]
            h = rect2[3]
        # establishing which rectangle is above the other
        if(rectObj1.topY > rectObj2.topY):
            topRect = rectObj1
            botRect = rectObj2
        else:
            topRect = rectObj2
            botRect = rectObj1
        # printing out values
        print('Top Rectangle Height: ' + topRect.h + ' Top Rectangle Width: ' + topRect.w)
        nt.putValue('TopRectHeight', topRect.h)
        nt.putValue('TopRectWidth', topRect.w)
        print('Bottom Rectangle Height: ' + botRect.h + ' Bottom Rectangle Width: ' + botRect.w)
        nt.putValue('BotRectHeight', botRect.h)
        nt.putValue('BotRectWidth', botRect.w)
        print('Total Height: ' + (topRect.topY - botRect.botY) + ' Total Width: ' + (botRect.rightX - topRect.leftX))
        nt.putValue('TotalHeight', (topRect.topY - botRect.botY))
        nt.putValue('TotalWidth', (botRect.rightX - topRect.leftX))
