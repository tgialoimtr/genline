# -*- coding: utf-8 -*-
'''
Created on Jun 5, 2018

@author: loitg
'''
import numpy as np

import pygame
import sys
import cv2
from textrender.font import TTFFont
from textrender.font2 import AccentedFont, UnicodeUtil
from textrender.relpos_matrix import RelPosSimple, RelPos4D
    
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
            self.charfont.overWrite(c, height, None, None)
#             self.charfont[c].setFont(None, height)
            if c == ' ':
                x0 += self.charfont.spaceWidth()
                continue
            if beforeChar is not None:
                temp = relposmat.at((beforeChar, c))
                spacing_hor = temp.hor
            else:
                spacing_hor = 0.0
            spacing_ver = relposmat.at((c, c)).ver              
            normHeight = self.charfont.normHeight()
            x0 += spacing_hor*normHeight
            charbb, charmask = self.charfont.render(c, (x0, y0 - spacing_ver*normHeight), surface.shape)
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
    def __init__(self, charset, params, accent_dir, vninfo_dir):
        self.charset = charset
        pf = TTFFont(charset, params['base-height'], params['base-font'])
        af = AccentedFont(pf, accent_dir, vninfo_dir)
        self.vneseinfo = UnicodeUtil(vninfo_dir)
        def bodau(ch):
            mch,_,_ = self.vneseinfo.decompose(ch)
            return mch
        self.bodau = bodau
        self.rd = RelPosRenderer(charset, af)
        self.params = params
        

    def overWriteFont(self, font_dict):
        for ch in self.charset:
            newheight=font_dict['detail-height'][ch] if 'detail-height' in font_dict and ch in font_dict['detail-height'] else font_dict['base-height']
            newbasefont=font_dict['detail-font'][ch] if 'detail-font' in font_dict and ch in font_dict['detail-font'] else font_dict['base-font']
            newratios=font_dict['detail-ratio'][ch] if 'detail-ratio' in font_dict and ch in font_dict['detail-ratio'] else font_dict['base-ratio']
            newratios = (newratios['x'], newratios['y'])
            self.rd.charfont.overWrite(ch, newheight=newheight, newbasefont=newbasefont, ratios=newratios)
    
    def overWriteRelPos(self, relpos_dict):
        base = relpos_dict['base-relpos-x']
        mat = RelPos4D(self.charset, base, bodau=self.bodau)
        if 'detail-relpos-x' in relpos_dict:
            for twochar, rpdist in relpos_dict['detail-relpos-x'].items():
                c1 = twochar[0]
                c2 = twochar[1]
                mat.mat[(c1,c2)].hor = (1.0 + rpdist) * base
        if 'relpos-y' in relpos_dict:
            for ch, rpheight in relpos_dict['relpos-y'].items():
                mat.mat[(ch,ch)].ver = rpheight
                
        self.mat = mat
    
    def overWriteRelPosAccent(self, accent_relpos_dict):
        relaccent = relpos_accent_dict['rel-accent']
        relchar = relpos_accent_dict['rel-char']
        for ch, charinfo in self.vneseinfo.accent_dict.items():
            mch, a0, a1 = charinfo.base, charinfo.accent0, charinfo.accent1
            a0 = str(a0); a1 = str(a1);
            temp = a0 + a1
            if temp in relaccent:
                pos0 = relchar[temp] if temp in relaccent else relchar['default']
                pos0 = (pos0['x'], pos0['y'])
                pos1 = (pos0[0] + relaccent[str(temp)]['x'], pos0[1] + relaccent[str(temp)]['y']) 
            else:
                pos0 = relchar[a0] if a0 in relchar else relchar['default']
                pos0 = (pos0['x'], pos0['y']) if a0 != '0' else None
                pos1 = relchar[a1] if a1 in relchar else relchar['default']
                pos1 = (pos1['x'], pos1['y']) if a1 != '0' else None
            self.rd.charfont.overWrite(ch, None, None, None, (pos0, pos1))
    
    def overWriteAccent(self, accent_dict):
        for accentid_str, info in accent_dict.items():
            accentid = int(accentid_str)
            if 'x0' not in info or 'y0' not in info:
                pos = None
            else:
                pos = (info['x0'],info['y0'])
            if 'rotation' not in info:
                info['rotation'] = 0.0
            if 'r_x' not in info or 'r_y' not in info:
                scale = (1.0,1.0)
            else:
                scale = (info['r_x'], info['r_y'])
            self.rd.charfont.accent_renderer.overWrite(accentid, info['default_height'], 
                                                       pos, info['rotation'], scale)

    def overWrite(self, **kwargs):
        for key in self.params:
            if key in kwargs and kwargs[key] is not None:
                self.params[key] = kwargs[key]
        
    def render(self, pos, shape, txt):
        (x,y) = pos
        mask, charmasks, charbbs = self.rd.render(txt, shape, y, 
                                                  self.params['height'], 
                                                  x, 
                                                  relposmat=self.mat)
        return mask, charmasks, charbbs

if __name__ == '__main__':
    import string
    params = {'txt':'123',
          'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/9thyssen.ttf',
          'base-height':30,
           'relpos-y':{},
           'angle':0.0,
           'height':30
           }
    renderer = TextRenderer(charset=string.ascii_letters + string.digits + ',.-', params=params,
                            accent_dir='/home/loitg/workspace/genline/resource/fontss/cmnd/chu_in/type_accent2',
                            vninfo_dir='/home/loitg/workspace/clocr/temp/diacritics2.csv')
    font_dict = {'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/9thyssen.ttf',
                   'detail-font':{'4':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/OFFSFOW.ttf',
                                 },
                   'base-height':30,
                   'detail-height':{'4':80},
                    'base-ratio':{'x':1.0,'y':1.0},
                    'detail-ratio':{
                                        '0':{'x':1.0,'y':1.2}
                                    }
                   }
    renderer.overWriteFont(font_dict)
    relpos_dict = {'base-relpos-x':0.3,
                      'detail-relpos-x': {'01':0.9,'12':0.9,'67':-0.5},
                      'relpos-y': {'1':0.0, '2':0.0}
                      }
    renderer.overWriteRelPos(relpos_dict)
    relpos_accent_dict = {'rel-accent':{
                                            '61':{'x':0.0,'y':0.0},
                                            '62':{'x':0.0,'y':0.0},
                                            '63':{'x':0.0,'y':0.0},
                                            '64':{'x':0.0,'y':0.0},
                                            '81':{'x':0.0,'y':0.0},
                                            '82':{'x':0.0,'y':0.0},
                                            '83':{'x':0.0,'y':0.0},
                                            '84':{'x':0.0,'y':0.0},
                                        },
                          'rel-char':{
                                            'default':{'x':-0.2,'y':0.2},
                                            '61':{'x':0.0,'y':0.0},
                                            '62':{'x':0.0,'y':0.0},
                                            '63':{'x':0.0,'y':0.0},
                                            '64':{'x':0.0,'y':0.0},
                                            '81':{'x':0.0,'y':0.0},
                                            '82':{'x':0.0,'y':0.0},
                                            '83':{'x':0.0,'y':0.0},
                                            '84':{'x':0.0,'y':0.0},
                                            '5':{'x':0.0,'y':-0.5},
                                        }
                          }
    renderer.overWriteRelPosAccent(relpos_accent_dict)
    
    accent_info = {'1':{'default_height':10},
                   '2':{'default_height':10},
                   '3':{'default_height':10},
                   '4':{'default_height':10},
                   '5':{'default_height':10},
                   '6':{'default_height':10},
                   '7':{'default_height':10},
                   '8':{'default_height':10},
                   '9':{'default_height':10}
                   }
    renderer.overWriteAccent(accent_info)
    mask,_,_ = renderer.render((0, 50), (100,300), u'SÂUSÉ,HỒ-ẨULỘ.')
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
    
    