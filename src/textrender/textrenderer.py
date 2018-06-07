'''
Created on Jun 5, 2018

@author: loitg
'''
import numpy as np

import pygame
import sys
import cv2
from char import PrintedChar, HandWrittenChar
from relpos_matrix import RelPosSimple, RelPos4D
    
class RelPosRenderer(object):
    
    def __init__(self, charset, charclass):
#         self.charset = charset
#         self.charfont = {}
        pass
        
    
    
    def render(self, txt, shape, ybaseline, height, x0, relposmat=None, relposmat2=None):           
        if relposmat is None:
            relposmat = RelPosSimple(0.0,0.0)
            
        surface = np.zeros(shape, dtype=np.uint8)
        beforeChar = txt[0]
        y0 = ybaseline     
        self.charfont[beforeChar].setFont(None, height)
        charbb, charmask = self.charfont[beforeChar].render((x0, y0), surface.shape)
        
#         print charmask.shape
#         print charmask.dtype
#         print surface.shape
#         print surface.dtype
        
        
        surface = cv2.bitwise_or(surface, charmask)
        charmasks = [charmask]
        charbbs = [charbb]
        for c in txt:
            self.charfont[c].setFont(None, height)
            if c == ' ':
                x0 += self.charfont[c].spaceWidth()
                continue
            temp = relposmat.at((beforeChar, c))
            spacing_hor = temp.hor
            spacing_ver = temp.ver
            normHeight = self.charfont[c].normHeight()
            dx = spacing_hor*normHeight
            dy = spacing_ver*normHeight
            charbb, charmask = self.charfont[c].render((x0 + dx, y0 + dy), surface.shape)
            surface = cv2.bitwise_or(surface, charmask)
            charmasks.append(charmask)
            x0 += charbb.width
            charbbs.append(np.array(charbb)) 
        return surface, charmasks, charbbs
            
            
    def renderFit(self, txt, height, relposmat=None, relposmat2=None):
        shape = (4*height, 200)
        ybaseline = height*2
        surface, charmasks, charbbs = self.render(txt, shape, ybaseline, height, 0, relposmat, relposmat2)
        
        #crop
        rect = pygame.Rect(charbbs[0])
        rect = rect.unionall(charbbs)
        
        pad = 0
        arr = surface; bbs = np.array(charbbs)
        
        rect = np.array(rect)
        rect[:2] -= pad
        rect[2:] += 2*pad
        print rect
        v0 = [max(0,rect[0]), max(0,rect[1])]
        print v0
        v1 = [min(arr.shape[1], rect[0]+rect[2]), min(arr.shape[0], rect[1]+rect[3])]
        print v1
        arr = arr[v0[1]:v1[1],v0[0]:v1[0],...]
        cv2.imwrite('/home/loitg/d.png', arr)
        charmasks = [mask[v0[1]:v1[1],v0[0]:v1[0],...] for mask in charmasks]
        for i in xrange(len(bbs)):
            bbs[i,0] -= v0[0]
            bbs[i,1] -= v0[1]
        ybaseline -= v0[0]
        return arr, charmasks, bbs, ybaseline
        


if __name__ == '__main__':

    pygame.init()
    
    
    charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
    
    rd = RelPosRenderer(charset, PrintedChar)
    
    ### FONTS
    basefont = '/home/loitg/Downloads/fonts/fontss/receipts/general_fairprice/PRINTF Regular.ttf'
    rd.charfont = {}
    for c in charset:
        rd.charfont[c] = PrintedChar(c)
        rd.charfont[c].setFont(basefont, 40)
    ### RelPos
    mat = RelPos4D(charset)
    mat.mat[('a','b')].hor = -0.5
    mat.mat[('1','2')].hor = +0.5
    
    txt = 'abc123'
    mask, charmasks, charbbs, _ = rd.renderFit(txt, 40, mat)
    
    cv2.imwrite('/home/loitg/a.png', mask)
    print 'done1'
    cv2.imshow('/home/loitg/b.png', charmasks[0])
    print 'done 2'
#     cv2.waitKey(-1)
    sys.exit(0)
    
    
    rd2 = RelPosRenderer(charset, HandWrittenChar)
    rd2.charfont = HandWrittenChar.createFromDB('') #<=== TODO
    ### RelPos
    mat = RelPosSimple()
    txt = 'abc123'
    mask, charmasks, charbbs = rd.render(txt, mat)
    
    cv2.imshow('rd', mask)
    cv2.imshow('rd0', charmasks[0])
    cv2.waitKey(-1)
    
    
    