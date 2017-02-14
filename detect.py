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

class App(tkinter.Frame):

    def __init__(self, master):
        super(App, self).__init__()
        frame = tkinter.Frame(master)
        frame.pack();
        
        self.angle = 0
        self.distance = 0
        self.eyes = 0
        
        self.image = None
        self.result = None
        
        self.camera = PiCamera()
        self.vis = ContourPipeline()
        self.imageHeight = 1232
        self.fovH = 48.8
        self.img_canvas = Canvas(frame, width="1200", height="300")
        self.img_canvas.grid(row=0, column=0, columnspan=6)
        
        Label(frame, text='Angle').grid(row=1, column=0, columnspan=1)
        self.angleLabel = Label(frame, text='a')
        self.angleLabel.grid(row=2, column=0, columnspan=1)
        
        Label(frame, text='Distance').grid(row=1, column=1, columnspan=1)
        self.distanceLabel = Label(frame, text='d')
        self.distanceLabel.grid(row=2, column=1, columnspan=1)
        
        Label(frame, text='looky thingy sees the thingy').grid(row=1, column=2, columnspan=1)
        self.eyesLabel = Label(frame, text='s')
        self.eyesLabel.grid(row=2, column=2, columnspan=1)
        
        Label(frame, text='height 1').grid(row=1, column=3, columnspan=1)
        self.height1Label = Label(frame, text='h1')
        self.height1Label.grid(row=2, column=3, columnspan=1)

        Label(frame, text='height 2').grid(row=1, column=4, columnspan=1)
        self.height2Label = Label(frame, text='h2')
        self.height2Label.grid(row=2, column=4, columnspan=1)

        Label(frame, text='width 1').grid(row=3, column=3, columnspan=1)
        self.width1Label = Label(frame, text='w1')
        self.width1Label.grid(row=4, column=3, columnspan=1)

        Label(frame, text='width 2').grid(row=3, column=4, columnspan=1)
        self.width2Label = Label(frame, text='w2')
        self.width2Label.grid(row=4, column=4, columnspan=1)

        Label(frame, text='total width').grid(row=3, column=2, columnspan=1)
        self.widthTotalLabel = Label(frame, text='wt')
        self.widthTotalLabel.grid(row=4, column=2, columnspan=1)
    def updateAngle(self, val):
        self.angle = val
    
    def updateDistance(self, val):
        self.distance = val
    
    def updateLookyThingy(self, val):
        self.eyes = val
    
    def updateImg(self):
        imgArray = PiRGBArray(self.camera, size=(1640, 1232))
        self.camera.resolution = (1640, 1232)
        self.camera.capture(imgArray, format="bgr", use_video_port=True)
        img = imgArray.array
        
        contours = self.vis.process(img)
        
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

        # declaring pink color for drawing bounding rectangle
        color = (150,170,255)
        result = img
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
                print(str(w) + ', ' + str(h))
                self.width1Label['text'] = str(w)
                self.height1Label['text'] = str(h)
            result = cv2.rectangle(img, rectObj1.pt1, rectObj1.pt2, color, thickness=3, lineType=8, shift=0)
        
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
                print(str(w) + ', ' + str(h))
                self.width2Label['text'] = str(w)
                self.height2Label['text'] = str(h)
            result = cv2.rectangle(img, rectObj2.pt1, rectObj2.pt2, color, thickness=3, lineType=8, shift=0)
        
        resizedImg = cv2.resize(result, (400, 300), interpolation=cv2.INTER_AREA)
        resizedImg = PImage.fromarray(resizedImg)
        resizedImg = ImageTk.PhotoImage(resizedImg)
        self.image = resizedImg
        
        
        
        self.img_canvas.create_image(200,150,image=self.image) #centered
        
        
        if(rect1Exists == True) and (rect2Exists == True):
            #result = PImage.fromarray(result)
            #result = ImageTk.PhotoImage(result)
            #self.result = result
            #self.img_canvas.create_image(1000,150,image=self.result) #centered
            if(rectObj1.pt1 < rectObj2.pt1):
                leftRect = rectObj1
                rightRect = rectObj2
            else:
                leftRect = rectObj2
                rightRect = rectObj1
            self.widthTotalLabel['text'] = str(rightRect.pt1[0] - leftRect.pt1[0])
            leftRatio = leftRect.h / self.imageHeight
            leftFocDist = 5 / leftRatio
            leftOpposite = leftFocDist / 2
            leftDist = leftOpposite / math.tan(math.radians(self.fovH / 2))

            rightRatio = rightRect.h / self.imageHeight
            rightFocDist = 5 / rightRatio
            rightOpposite = rightFocDist / 2
            rightDist = rightOpposite / math.tan(math.radians(self.fovH / 2))

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
                if(leftDist < rightDist):
                    angle *= -1
                print(str(angle))
                self.angleLabel['text'] = angle
                self.distanceLabel['text'] = middleDist
                self.eyesLabel['text'] = 'True'
            else:
                angle = 0
                self.angleLabel['text'] = angle
                self.distanceLabel['text'] = middleDist
                self.eyesLabel['text'] = 'True'
        else:
            self.eyesLabel['text'] = 'False'
            self.angleLabel['text'] = 'N/A'
            self.distanceLabel['text'] = 'N/A'
        
        root.after(250, self.updateImg)
        

root = tkinter.Tk()
root.wm_title('Color Object Detection')
app = App(root)
root.geometry("1250x500+0+0")
root.after(250, app.updateImg)
root.mainloop()


# camera.close()
