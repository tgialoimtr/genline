'''
Created on Jun 5, 2018

@author: loitg
'''
import numpy as np

import pygame
import sys
import cv2
from textrender.font import TTFFont
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
        
class TextRenderer(object):
    def __init__(self, charset, params):
        self.charset = charset        
        pf = TTFFont(charset, params['base-height'], params['base-font'])
        self.rd = RelPosRenderer(charset, pf)
        self.params = params

    def overWriteFont(self, font_dict):
        for ch in self.charset:
            newheight=font_dict['detail-height'][ch] if 'detail-height' in font_dict and ch in font_dict['detail-height'] else None
            newbasefont=font_dict['detail-font'][ch] if 'detail-font' in font_dict and ch in font_dict['detail-font'] else None
            if newbasefont is not None or newheight is not None:
                print ch, newheight, newbasefont
                self.rd.charfont.overWrite(ch, newheight=newheight, newbasefont=newbasefont)
    
    def overWriteRelPosX(self, relposx_dict):
        base = relposx_dict['base-relpos']
        mat = RelPos4D(self.charset, base)
        if 'detail-relpos' in relposx_dict:
            for twochar, rpdist in relposx_dict['detail-relpos'].iteritems():
                c1 = twochar[0]
                c2 = twochar[1]
                mat.mat[(c1,c2)].hor = (1.0 + rpdist) * base
        
        self.mat = mat
    
    def overWrite(self, **kwargs):
        for key in self.params:
            if key in kwargs and kwargs[key] is not None:
                self.params[key] = kwargs[key]
        
    def render(self, (x,y), shape, txt):
        mask, charmasks, charbbs = self.rd.render(txt, shape, y, 
                                                  self.params['height'], 
                                                  x, 
                                                  relposmat=self.mat)
        return mask, charmasks, charbbs
        
if __name__ == '__main__':
    params = {'txt':'123',
          'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/9thyssen.ttf',
          'base-height':30,
           'relpos-y':{},
           'angle':0.0,
           'height':30
           }
    renderer = TextRenderer(charset='0123456789', params=params)
    font_dict = {'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/9thyssen.ttf',
                   'detail-font':{'4':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/OFFSFOW.ttf',
                                 },
                   'base-height':30,
                   'detail-height':{'4':80}
                   }
    renderer.overWriteFont(font_dict)
    relposx_dict = {'base-relpos':0.3,
                      'detail-relpos': {'01':0.9,'12':0.9,'67':-0.5}
                      }
    renderer.overWriteRelPosX(relposx_dict)
    mask,_,_ = renderer.render((0, 50), (100,300), '01234567')
    cv2.imshow('hh', mask)
    cv2.waitKey(-1)
    
# if __name__ == '__main__':
#     charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
#      
#     ### FONTS
#     basefont = '/home/loitg/Downloads/fonts/fontss/receipts/general_fairprice/LEFFC2.TTF'
#     ### RelPos
#     mat = RelPos4D(charset)
#     mat.mat[('a','b')].hor = -0.1
#     mat.mat[('1','2')].hor = +0.5
#     
#     pf = TTFFont(charset, 40, basefont)
#     rd = RelPosRenderer(charset, pf)
#     
#     txt = 'abc123mn'
#     mask, charmasks, charbbs, ybaseline = rd.renderFit(txt, 40, mat)
#     cv2.imshow('mask', mask)
#     for img, bb in zip(charmasks,charbbs):
#         cv2.imshow('mask0', img)
#         aaa = mask[bb[1]:(bb[1]+bb[3]), bb[0]:(bb[0]+bb[2])]
#         cv2.imshow('bb0', aaa)
#         cv2.waitKey(-1)
#     sys.exit(0)
#     rd2 = RelPosRenderer(charset, HandWrittenChar)
#     rd2.charfont = HandWrittenChar.createFromDB('/home/loitg/ocr/by_write/', "NIST")
#     ### RelPos
#     mat = RelPosSimple()
#     txt = 'abc123'
#     mask, charmasks, charbbs = rd2.renderFit(txt, mat)
#     
#     cv2.imshow('rd', mask)
#     cv2.imshow('rd0', charmasks[0])
#     cv2.waitKey(-1)
#     
    
    