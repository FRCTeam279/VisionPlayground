#!/usr/bin/python3
from PIL import Image as PImage
from PIL import ImageTk
import tkinter
from tkinter import *
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np
import imutils
import cv2




class App(tkinter.Frame):

    def __init__(self, master):
        super(App, self).__init__()
        frame = tkinter.Frame(master)
        frame.pack();

        self.camera = PiCamera()
        
        self.h_lower = 0
        self.s_lower = 0
        self.v_lower = 0
        self.h_upper = 0
        self.s_upper = 0
        self.v_upper = 0
                      
        self.image = None
        self.resultGray = None
        self.result = None
        
        self.img_canvas = Canvas(frame, width="1200", height="300")
        self.img_canvas.grid(row=0, column=0, columnspan=6)
        
        processImgBtn = Button(frame, text="Update", command=self.updateImg)
        processImgBtn.grid(row=5, column=0, columnspan=6)

        Label(frame, text='H Lower').grid(row=2, column=0)
        scaleHLower = Scale(frame, from_=0, to=179, orient=HORIZONTAL, command=self.updateHLower)
        scaleHLower.grid(row=2, column=1)
        Label(frame, text='H Upper').grid(row=3, column=0)
        scaleHUpper = Scale(frame, from_=0, to=179, orient=HORIZONTAL, command=self.updateHUpper)
        scaleHUpper.grid(row=3, column=1)

        Label(frame, text='S Lower').grid(row=2, column=2)
        scaleSLower = Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=self.updateSLower)
        scaleSLower.grid(row=2, column=3)
        Label(frame, text='S Upper').grid(row=3, column=2)
        scaleSUpper = Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=self.updateSUpper)
        scaleSUpper.grid(row=3, column=3)

        Label(frame, text='V Lower').grid(row=2, column=4)
        scaleVLower = Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=self.updateVLower)
        scaleVLower.grid(row=2, column=5)
        Label(frame, text='V Upper').grid(row=3, column=4)
        scaleVUpper = Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=self.updateVUpper)
        scaleVUpper.grid(row=3, column=5)

        self.hRangeLabel = Label(frame, text='h')
        self.hRangeLabel.grid(row=4, column=0, columnspan=2)
        
        self.sRangeLabel = Label(frame, text='s')
        self.sRangeLabel.grid(row=4, column=2, columnspan=2)
        
        self.vRangeLabel = Label(frame, text='v')
        self.vRangeLabel.grid(row=4, column=4, columnspan=2)


    def updateHLower(self, val):
        self.h_lower = val
    
    def updateHUpper(self, val):
        self.h_upper = val
    
    def updateSLower(self, val):
        self.s_lower = val
    
    def updateSUpper(self, val):
        self.s_upper = val
    
    def updateVLower(self, val):
        self.v_lower = val
    
    def updateVUpper(self, val):
        self.v_upper = val
    
    
    def updateImg(self):
        #get image
        imgArray = PiRGBArray(self.camera, size=(400, 300))
        self.camera.capture(imgArray, format="bgr", resize=(400, 300), use_video_port=True)
        img = imgArray.array
        #img = cv2.GaussianBlur(img, (5,5), 0)
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower = np.array([self.h_lower, self.s_lower, self.v_lower], dtype=int)
        upper = np.array([self.h_upper, self.s_upper, self.v_upper], dtype=int)

        self.hRangeLabel['text'] = self.h_lower + " - " + self.h_upper
        self.sRangeLabel['text'] = self.s_lower + " - " + self.s_upper
        self.vRangeLabel['text'] = self.v_lower + " - " + self.v_upper
        
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(img, img, mask=mask)
        
        
        resultGray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        ret, resultGray = cv2.threshold(resultGray, 100, 255, 0, cv2.THRESH_BINARY)
        resultGray, contours, hierarchy = cv2.findContours(resultGray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


        for c in contours:
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(result, [box], 0, (0,0,255), 2)
        
    
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = PImage.fromarray(img)
        img = ImageTk.PhotoImage(img)
        self.image = img
        
        resultGray = cv2.cvtColor(resultGray, cv2.COLOR_GRAY2RGB)
        resultGray = PImage.fromarray(resultGray)
        resultGray = ImageTk.PhotoImage(resultGray)
        self.resultGray = resultGray
        
        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        result = PImage.fromarray(result)
        result = ImageTk.PhotoImage(result)
        self.result = result
        
        self.img_canvas.create_image(200,150,image=self.image) #centered
        self.img_canvas.create_image(600,150,image=self.resultGray) #centered
        self.img_canvas.create_image(1000,150,image=self.result) #centered
        root.after(250, self.updateImg)
        
		
root = tkinter.Tk()
root.wm_title('Color Object Detection')
app = App(root)
root.geometry("1250x500+0+0")
root.after(250, app.updateImg)
root.mainloop()

print('Shutting down and cleaning up')

    

