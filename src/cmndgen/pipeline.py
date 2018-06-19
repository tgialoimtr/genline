'''
Created on Jun 5, 2018

@author: loitg
'''
import cv2
import sys
import numpy as np
from paramatch.collections import Params
from textrender.textrenderer import RelPosRenderer
from textrender.font import TTFFont
from textrender.relpos_matrix import RelPos4D

class CMNDPipeline(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        self.txt = '123'
        self.params = Params()        
        
        ### FONTS
        self.charset = '0123456789'
        basefont = '/home/loitg/Downloads/fonts/fontss/receipts/general_fairprice/LEFFC2.TTF'
        self.charfont = TTFFont(self.charset, 40, basefont)
        ### RelPos
        self.mat = RelPos4D(self.charset)
        self.mat.mat[('a','b')].hor = -0.1
        self.mat.mat[('1','2')].hor = +0.5
        
        
        self.renderer = RelPosRenderer(self.charset, self.charfont)
        self.renderer.a = self.params.new()
        
 
        
    def gen(self):
        mask, charmasks, charbbs, ybaseline = self.renderer.renderFit(self.txt, 40, self.mat)

        return line
    
    
    
if __name__ == '__main__':

    cv2.imshow('mask', mask)
    for img, bb in zip(charmasks,charbbs):
        cv2.imshow('mask0', img)
        aaa = mask[bb[1]:(bb[1]+bb[3]), bb[0]:(bb[0]+bb[2])]
        cv2.imshow('bb0', aaa)
        cv2.waitKey(-1)
    sys.exit(0)