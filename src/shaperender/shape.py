'''
Created on Jun 23, 2018

@author: loitg
'''

import cv2
import numpy as np
import math, random

# class SVGShape(object):
#     
#     def __init__(self, params):
#         pass
#     
# class PNGShape(object):
# 
#     def __init__(self, pngfile):
#         self.img = cv2.imread(pngfile)


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

    def __init__(self):
        self.params = {'height':30,
                       'amp':3,
                       'wavelength':30,
                       'length':200,
                       'angle':0.0,
                       'thick':1
                       }
        
    def overWrite(self, **kwargs):
        for key in self.params:
            if key in kwargs and kwargs[key] is not None:
                self.params[key] = kwargs[key]
        
    def render(self, (x,y), shape):
        x = int(x)
        y = int(y)
        alpha= np.zeros(shape,'uint8')
        dy = self.params['height']*1.0/5
        x0 = x
        y0 = y - int(self.params['height'])/2
        amp = self.params['amp']
        wavelength = int(self.params['wavelength'])
        length = int(self.params['length'])
        phase = random.randint(0, 360)
        thick = int(self.params['thick'])
        for i in range(6):
            pts = sineWave(x0, int(i*dy + y0), length, amp, wavelength, phase=phase)
            cv2.polylines(alpha, [pts], isClosed=False, color=255, thickness=thick)
        rotM = cv2.getRotationMatrix2D((x0,y0),self.params['angle'],1)
        alpha = cv2.warpAffine(alpha,rotM,(alpha.shape[1], alpha.shape[0]))
        
        return alpha      

class BGDummyGui(object):

    def __init__(self):
        self.params = {}
    
    def overWrite(self, **kwargs):# width, height, ...
        for key, value in kwargs.iteritems():
            if value is not None and key in self.params:
                self.params[key] = value
                
    
    def render(self, (x,y), shape):
        alpha= np.zeros(shape,'uint8')
        amp = random.randint(shape[0]/7, shape[0]/5)
        wavelength = random.randint(shape[0]/4, shape[0]/2)
        thick = random.randint(1,2)
        angle= random.uniform(0.0, 160.0)
        n = random.randint(15,30)
        y0 = random.randint(20,30)
        dy = (shape[0] - y0)/n
        x0 = random.randint(20,30)
        dx = (shape[1] - x0)/n
        
        for i in range(n):
            x0 += dx + random.randint(-2,2)
            y0 += dy + random.randint(-2,2)
            pts = sineWave(x0, y0, int(shape[1]*0.8), amp, wavelength, angle)
            cv2.polylines(alpha, [pts], isClosed=False, color=255, thickness=thick)
        
        return alpha
  
        
class CMNDCircle(object):
    def __init__(self):
        self.params = {'R1':80,
                       'R2':100,
                       'a1':10,
                       'a2':30,
                       'n':30, # number on circles
                       'thick':1
                       }
    def overWrite(self, **kwargs):
        for key in self.params:
            if key in kwargs and kwargs[key] is not None:
                self.params[key] = kwargs[key]
                
    def render(self, (x,y), shape):
        x = int(x)
        y = int(y)
        alpha= np.zeros(shape,'uint8')
        R1 = self.params['R1']
        R2 = self.params['R2']
        a1 = math.pi * self.params['a1']/180.0
        a2 = math.pi * self.params['a2']/180.0
        n = int(self.params['n'])
        thick = int(self.params['thick'])
        da = 2.0*math.pi/n
        for i in range(n):
            a1 += da; a2 += da
            x0 = x + int(R1*math.cos(a1)); y0 = y + int(R1*math.sin(a1))
            x1 = x + int(R2*math.cos(a2)); y1 = y + int(R2*math.sin(a2))
            cv2.line(alpha, (x0,y0), (x1,y1), color=255, thickness=thick)
            
            x0 = x + int(R1*math.cos(a2)); y0 = y + int(R1*math.sin(a2))
            x1 = x + int(R2*math.cos(a1)); y1 = y + int(R2*math.sin(a1))
            cv2.line(alpha, (x0,y0), (x1,y1), color=255, thickness=thick)           
            
        return alpha


if __name__ == "__main__":
    shape1 = CMNDCircle()
    shape1.overWrite(R1=100, R2=140)
    shape1.overWrite()
    for i in range(10):
        mask = shape1.render((150,150), (300,300))
        cv2.imshow('hh', mask)
        cv2.waitKey(-1)
    
    
    
    