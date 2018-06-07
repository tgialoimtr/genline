'''
Created on Jun 5, 2018

@author: loitg
'''
import numpy as np

import sys
import cv2
from char import PrintedChar, HandWrittenChar
from relpos_matrix import RelPosSimple, RelPos4D

class RelPosRenderer(object):
    
    def __init__(self, charset, charclass):
#         self.charset = charset
#         self.charfont = {}
        pass
        
    
    
    def render(self, txt, relposmat=None, relposmat2=None):           
        if relposmat is None:
            relposmat = RelPosSimple(0.0,0.0)
            
        surface = np.zeros(self.shape)
        beforeChar = txt[0]
        charbb, charmask = self.charfont[beforeChar].putAt((x0, y0), surface)
        surface = cv2.bitwise_or(surface, charmask)
        charmasks = [charmask]
        charbbs = [charbb]
        for c in txt:
            if c == ' ':
                x0 += self.charfont[c].spaceWidth()
                continue
            temp = relposmat.at((beforeChar, c))
            spacing_hor = temp.hor
            spacing_ver = temp.ver
            normHeight = self.charfont[c].normHeight()
            dx = spacing_hor*normHeight
            dy = spacing_ver*normHeight
            charbb, charmask = self.charfont[c].putAt((x0 + dx, y0 + dy), surface)
            surface = cv2.bitwise_or(surface, charmask)
            charmasks.append(charmask)
            charbbs.append(charbb)
            
            x0 += charbb.width
        return surface, charmasks, charbbs, ybaseline, height
            
            



if __name__ == '__main__':
    import pygame
    pygame.init()
    
    
    charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
    
    rd = RelPosRenderer(charset, PrintedChar)
    
    ### FONTS
    basefont = '/home/loitg/Downloads/fonts/fontss/receipts/general_fairprice/PRINTF Regular.ttf'
    rd.charfont = {}
    for c in charset:
        rd.charfont[c] = PrintedChar()
        rd.charfont[c].setFont(basefont, 40)
    ### RelPos
    mat = RelPos4D(charset)
    mat.mat[('a','b')].hor = -0.5
    mat.mat[('1','2')].hor = +0.5
    
    txt = 'abc123'
    mask, charmasks, charbbs = rd.render(txt, mat)
    
    cv2.imshow('rd', mask)
    cv2.imshow('rd0', charmasks[0])
    cv2.waitKey(-1)
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
    
    
    