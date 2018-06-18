'''
Created on Jun 5, 2018

@author: loitg
'''
import numpy as np

import pygame
import sys
import cv2
from font import TTFFont
from relpos_matrix import RelPosSimple, RelPos4D
    
class RelPosRenderer(object):
    
    def __init__(self, charset, charfont=None):
        self.charfont = charfont
        
    
    
    def render(self, txt, shape, ybaseline, height, x0, relposmat=None, relposmat2=None):           
        if relposmat is None:
            relposmat = RelPosSimple(0.0,0.0)
            
        surface = np.zeros(shape, dtype=np.uint8)
        beforeChar = None
        y0 = ybaseline
        charmasks = []
        charbbs = []
        for c in txt:
            self.charfont.overWrite(c, height, None)
#             self.charfont[c].setFont(None, height)
            if c == ' ':
                x0 += self.charfont.spaceWidth()
                continue
            if beforeChar is not None:
                temp = relposmat.at((beforeChar, c))
                spacing_hor = temp.hor
                spacing_ver = temp.ver
            else:
                spacing_hor = 0.0
                spacing_ver = 0.0                
            normHeight = self.charfont.normHeight()
            x0 += spacing_hor*normHeight
            y0 += spacing_ver*normHeight
            charbb, charmask = self.charfont.render(c, (x0, y0), surface.shape)
            surface = cv2.bitwise_or(surface, charmask)
            charmasks.append(charmask)
            x0 += charbb.width
            charbbs.append(np.array(charbb))
            beforeChar = c
        return surface, charmasks, charbbs
            
            
    def renderFit(self, txt, height, relposmat=None, relposmat2=None):
        shape = (4*height, 200)
        ybaseline = 2*height
        surface, charmasks, charbbs = self.render(txt, shape, ybaseline, height, 0, relposmat, relposmat2)
        
        #crop
        rect = pygame.Rect(charbbs[0])
        rect = rect.unionall(charbbs)
        
        pad = 0
        arr = surface
        bbs = charbbs
        
        rect = np.array(rect)
        rect[:2] -= pad
        rect[2:] += 2*pad
        v0 = [max(0,rect[0]), max(0,rect[1])]
        v1 = [min(arr.shape[1], rect[0]+rect[2]), min(arr.shape[0], rect[1]+rect[3])]
        arr = arr[v0[1]:v1[1],v0[0]:v1[0],...]
        charmasks = [mask[v0[1]:v1[1],v0[0]:v1[0],...] for mask in charmasks]
        for bb in bbs:
            bb[0] -= v0[0]
            bb[1] -= v0[1]
        ybaseline -= v0[1]
        return arr, charmasks, bbs, ybaseline
        


if __name__ == '__main__':
    charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
     
    ### FONTS
    basefont = '/home/loitg/Downloads/fonts/fontss/receipts/general_fairprice/LEFFC2.TTF'
    ### RelPos
    mat = RelPos4D(charset)
    mat.mat[('a','b')].hor = -0.1
    mat.mat[('1','2')].hor = +0.5
    
    pf = TTFFont(charset, 40, basefont)
    rd = RelPosRenderer(charset, pf)
    
    txt = 'abc123mn'
    mask, charmasks, charbbs, ybaseline = rd.renderFit(txt, 40, mat)
    cv2.imshow('mask', mask)
    for img, bb in zip(charmasks,charbbs):
        cv2.imshow('mask0', img)
        aaa = mask[bb[1]:(bb[1]+bb[3]), bb[0]:(bb[0]+bb[2])]
        cv2.imshow('bb0', aaa)
        cv2.waitKey(-1)
    sys.exit(0)
    
    
    rd2 = RelPosRenderer(charset, HandWrittenChar)
    rd2.charfont = HandWrittenChar.createFromDB('/home/loitg/ocr/by_write/', "NIST")
    ### RelPos
    mat = RelPosSimple()
    txt = 'abc123'
    mask, charmasks, charbbs = rd2.renderFit(txt, mat)
    
    cv2.imshow('rd', mask)
    cv2.imshow('rd0', charmasks[0])
    cv2.waitKey(-1)
    
    
    