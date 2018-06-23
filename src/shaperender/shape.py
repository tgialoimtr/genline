'''
Created on Jun 23, 2018

@author: loitg
'''

import cv2
import numpy as np
import math, random


def sineWave(x0, y0, length, amp, wavelength, angle=0, phase=0):
    x = np.arange(x0 - length/2, x0 + length/2, 2)
    B = np.array(x, 'float')
    o = np.ones_like(B, float)
    for i, xx in enumerate(x):
        B[i] = math.sin(2.0*math.pi*(xx-x[0])/wavelength + phase)
    B *= amp
    B += y0
    datapoints = np.vstack((x,B,o))
    rotM = cv2.getRotationMatrix2D((x0,y0),angle,1)
    datapoints = rotM.dot(datapoints)
    datapoints = datapoints[:2,].astype(np.int32).T
    return datapoints

class BGGuiCMNDSo(object):

    def __init__(self, params):
        pass
    def overWrite(self, **kwargs):# width, height, ...
        pass
    def render(self, (x,y), shape):
        ret= np.zeros(shape=shape)
    def buildGuillocheBGSo(self, height, angel):
        alpha= np.zeros((self.height, self.width),'uint8')
        dy = height*1.0/5
        x0 = self.x0
        y0 = self.y0 - height/2
        amp = self.p['gui_amp']
        wavelength = self.p.new('wavelength', dy*4, freeze=True).x
        length = self.p.new('length', self.height*7, paramrange=(self.height*5, self.height*9), freeze=True).x
        phase = random.randint(0, 360)
        thick = random.randint(1, 2)
        for i in range(6):
            pts = self.sineWave(x0, int(i*dy + y0), length, amp, wavelength, phase=phase)
            cv2.polylines(alpha, [pts], isClosed=False, color=255, thickness=thick)
        rotM = cv2.getRotationMatrix2D((x0,y0),angel,1)
        alpha = cv2.warpAffine(alpha,rotM,(alpha.shape[1], alpha.shape[0]))
        
        return alpha      

class BGDummyGui(object):

    def __init__(self, params):
        self.params = {}
    
    def overWrite(self, **kwargs):# width, height, ...
        for key, value in kwargs.iteritems():
            if value is not None and key in self.params:
                self.params[key] = value
                
    
    def render(self, (x,y), shape):
        alpha= np.zeros(shape,'uint8')
        amp = self.params['amp'] # random.randint(self.height/7, self.height/5)
        wavelength = random.randint(self.height/4, self.height/2)
        thick = random.randint(1,2)
        angle= random.uniform(0.0, 160.0)
        n = random.randint(15,30)
        y0 = random.randint(20,30)
        dy = (self.height - y0)/n
        x0 = random.randint(20,30)
        dx = (self.width - x0)/n
        
        for i in range(n):
            x0 += dx + random.randint(-2,2)
            y0 += dy + random.randint(-2,2)
            pts = sineWave(x0, y0, int(self.width*0.8), amp, wavelength, angle)
            cv2.polylines(alpha, [pts], isClosed=False, color=255, thickness=thick)
        
        return alpha
  
        
class CMNDCircle(object):


    def __init__(self, params):
        pass
    def overWrite(self, **kwargs):# width, height, ...
        pass
    def render(self, (x,y), shape):
        ret= np.zeros(shape=shape)    
    
# class SVGShape(object):
#     
#     def __init__(self, params):
#         pass
#     
# class PNGShape(object):
# 
#     def __init__(self, pngfile):
#         self.img = cv2.imread(pngfile)


if __name__ == "__main__":
    shape1 = BGDummyGui()
    shape1.overWrite(angle=0, n=20)
    mask = shape1.render((10,10), (100,100))
    cv2.imshow('hh', mask)
    cv2.waitKey(-1)
    
    
    
    