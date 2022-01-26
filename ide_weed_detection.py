import cv2
import sys
import numpy as np
import glob
import time
'''import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT) x led
GPIO.setup(7, GPIO.OUT)y led
GPIO.setup(3, GPIO.OUT)z led'''

class WeedDetection:
    def __init__(self,img):
        self.height = img.shape[0]
        self.width = img.shape[1]
        self.part_width = img.shape[1]//3
    
    def preprocess(self, img):
        '''
        Blurs image and converts to HSV color scale for better detection of the weeds
        '''
        #blur image
        img_blur = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)
        #convert to HSV color scale
        img_hsv = cv2.cvtColor(img_blur,cv2.COLOR_BGR2HSV)
    
        return img_hsv

    def createMask(self, img_hsv):
        '''
        Create a mask containing only green colored pixels
        '''
        h=img_hsv[:, :, 0]

        #create mask
        msk = cv2.inRange(h,30,80)
        cv2.imshow('msk',msk)
        
        return msk

    def transform(self, msk):
        '''
        Perform morphology transformation in the binary image
        '''
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))

        #erosion and dilation
        res_msk = cv2.morphologyEx(msk, cv2.MORPH_OPEN, kernel)
        res_msk = cv2.morphologyEx(res_msk, cv2.MORPH_CLOSE, kernel)

        return res_msk

    def calcPercentage(self, msk):
        '''
        returns the percentage of white in a binary image
        '''
        height, width = msk.shape[:2]
        num_pixels = height * width
        count_white = cv2.countNonZero(msk)
        percent_white = (count_white/num_pixels) * 100
        percent_white = round(percent_white,2)

        return percent_white

    def weedPercentage(self, msk):
        '''
        Divide the mask into 3 parts and calculate the percentage of weeds in each part
        This will be used to find the direction in which the bot has to move
        '''
        left_part = msk[:,:self.part_width]
        mid_part = msk[:,self.part_width:2*self.part_width]
        right_part = msk[:,2*self.part_width:]

        #percentage of weed
        left_percent = self.calcPercentage(left_part)
        mid_percent = self.calcPercentage(mid_part)
        right_percent = self.calcPercentage(right_part)

        return [left_percent, mid_percent, right_percent]

    def markPercentage(self, img, percentage):
        '''
        takes a 3-element list containing the left, middle and right percentages and writes them to an image
        '''
        part_width = self.width//3

        font = cv2.FONT_HERSHEY_SIMPLEX

        #write text in each partition
        for i in range(3):
            cv2.putText(img, str(percentage[i]) + "%", (int(part_width*(i + 0.14)), self.height//2), font, 0.75, (0,0,255), 2, cv2.LINE_AA)
        return img

def main():
  
    #img = cv2.imread('i5.jpeg')
    img = cv2.imread('weed.jpg')

    img_resize = cv2.resize(img, (750,500))

    wd = WeedDetection(img)

    img_hsv = wd.preprocess(img)

    msk = wd.createMask(img_hsv)

    msk = wd.transform(msk)

    percentage = wd.weedPercentage(msk)
    res =wd.markPercentage(img_resize, percentage)
    res_msk = cv2.bitwise_and(img,img,mask = msk)
    z=percentage[2]
    y=percentage[1]
    x=percentage[0]
    if (x==y and y==z):
        print('x,y,z leds on')
        
    if (x==y and x>z) :
        print('x,y is on')
     
    if (y==z and z>x) :
        print('y,z is on')
     
    if (x==z and z>y) :
        print('x,z is on')

    if (x>y and x>z):
        print('x led on')
     
    if (y>z and y>x) :
        print('y led on')
     
    if (z>x and z>y):
        print('z led on')

    cv2.imshow('Res',res)
    cv2.imshow('Mask', res_msk)
    cv2.imshow('binary',msk)
    cv2.imshow('Frame',img)
    cv2.waitKey()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
