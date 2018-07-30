# -*- coding: utf-8 -*-
'''
Created on Jul 26, 2018

@author: loitg
'''
import cv2
import numpy as np
import random
import os, string
from glob import glob
from textrender.font import TTFFont
from utils.common import putRect
import pygame

def findBoundBox(mask):
    return None

class VNCharInfo(object):
    def __init__(self, base, accent0, accent1):
        self.base = base
        self.accent0 = accent0
        self.accent1 = accent1
        
class UnicodeUtil(object):
    def __init__(self, diacritics_path_csv):
        self.accent_dict = {}
        self.accent_set = set()
        with open(diacritics_path_csv) as f:
            for line in f:
                temp = line.strip().split(',')
                accent = temp[1].decode('utf8')                
                self.accent_dict[accent] = VNCharInfo(temp[2], temp[3], temp[4])
                self.accent_set.add(int(temp[3]))
                self.accent_set.add(int(temp[4]))
    
    def charList(self):
        return list(self.accent_dict.keys())
    
    def accentList(self):
        return list(self.accent_set)
    
    def decompose(self, ch):
        if ch in self.accent_dict:
            info = self.accent_dict[ch]
            return info.base, info.accent0, info.accent1
        else:
            return ch, 0, 0
    
    def compose(self, mch, a0, a1=0):
        for ch, charinfo in self.accent_dict.items():
            if charinfo.base != mch: continue
            if charinfo.accent0 != a0: continue
            if charinfo.accent1 != a1: continue
            return ch
        
    def at(self, ch):
        if ch in self.accent_dict:
            return self.accent_dict[ch]
        else:
            return VNCharInfo(ch, 0, 0)
        

class MultipleMaskLoader(object):
    '''
    All-On-RAM Loader
    '''
    def __init__(self, white_bg=False, binary_mask=True):
        self.maskdict = {}
        self.white_bg = white_bg
        self.binary_mask = binary_mask
    
    def addMask(self, maskid, imgdir):
        for fn in os.listdir(imgdir):
            if self.binary_mask:
                temp = cv2.imread(os.path.join(imgdir,fn),0)
            else:
                temp = cv2.imread(os.path.join(imgdir,fn))
            if self.white_bg:
                temp = np.where(temp > 128, np.uint8(0), np.uint8(255))
            else:
                temp = np.where(temp > 128, np.uint8(255), np.uint8(0))
            boundbox = None
            if maskid not in self.maskdict:
                self.maskdict[maskid] = []
            self.maskdict[maskid].append((temp, boundbox))
        
    def getMask(self, maskid):
        if maskid in self.maskdict:
            return random.choice(self.maskdict[maskid])
        else:
            return None

class ShapeInfo(object):
    def __init__(self):
        pass
    

class MaskRender(object):
    
    def __init__(self, maskloader, pos_mode='CENTER', maskid_list=set()):
        self.maskloader = maskloader
        self.info = {}
        for maskid in maskid_list:
            self.overWrite(maskid)
        self.pos_mode = pos_mode
    
    def overWrite(self, accentid, default_height=10, realorigin=None, rotation=0.0, scale=(1.0, 1.0)):
        if accentid not in self.info:
            self.info[accentid] = ShapeInfo()
        self.info[accentid].default_height = default_height
        self.info[accentid].realorigin = realorigin
        self.info[accentid].rotation = rotation
        self.info[accentid].r_x = scale[0]
        self.info[accentid].r_y = scale[1]
                  
    def render(self, accentid, pos, shape=None):
        info = self.info[accentid]
        mask, _ = self.maskloader.getMask(accentid)
        M = cv2.getRotationMatrix2D((mask.shape[1]/2,mask.shape[0]/2),info.rotation,1)
        mask = cv2.warpAffine(mask,M,(mask.shape[1],mask.shape[0]))
        newwidth = int(1.0*mask.shape[1]/mask.shape[0]*info.default_height)
        mask = cv2.resize(mask,(newwidth, info.default_height))
        if info.realorigin is None:
            x=int(pos[0]) - mask.shape[1]/2
            y=int(pos[1]) - mask.shape[0]/2
        else:
            x=int(pos[0]) - info.realorigin[0]
            y=int(pos[1]) - info.realorigin[1]
        rs = np.zeros(shape=shape, dtype=np.uint8)
        mask = putRect(rs, mask, (x,y))
        if info.r_x != 1.0 or info.r_y != 1.0:
            mask9 = cv2.resize(mask, None, fx=info.r_x, fy=info.r_y)
            x9 = int(round(x*info.r_x))
            y9 = int(round(y*info.r_y))
            x0 = 0 - x; x1 = mask.shape[1] - x; y0 = 0 - y; y1 = mask.shape[0] - y;
            x90 = 0 - x9; x91 = mask9.shape[1] - x9; y90 = 0 - y9; y91 = mask9.shape[0] - y9;
            newx0 = max(x0, x90); newx1 = min(x1,x91);
            newy0 = max(y0, y90); newy1 = min(y1,y91);
            x0 = newx0 + x; x1 = newx1 + x; y0 = newy0 + y; y1 = newy1 + y;
            x90 = newx0 + x9; x91 = newx1 + x9; y90 = newy0 + y9; y91 = newy1 + y9;
            mask[:,:] = 0
            mask[y0:y1,x0:x1] = mask9[y90:y91,x90:x91]
        return findBoundBox(mask), mask
    
    



class AccentedFont(object):

    def __init__(self, mainfont, accent_dir, vneseinfo_file):
        self.mfont = mainfont
        self.vneseinfo = UnicodeUtil(vneseinfo_file)
        accent_loader = MultipleMaskLoader(white_bg=True)
        for i in range(1,10):
            accent_loader.addMask(i, os.path.join(accent_dir, str(i)))
        accent_render = MaskRender(accent_loader, maskid_list=self.vneseinfo.accentList())
        self.accent_renderer = accent_render
        self.mat = {}
        for mch in self.mfont.charset:
            self.mat[mch] = None, None
        for ch in self.vneseinfo.charList():
            self.mat[ch] = None, None
        
    def overWrite(self, ch, newheight=None, newbasefont=None, ratios=None, pos=None):
        if pos is not None:
            self.mat[ch] = pos
        if newheight is not None or newbasefont is not None or ratios is not None:
            mch, _, _ = self.vneseinfo.decompose(ch)
            self.mfont.overWrite(mch, newheight, newbasefont, ratios)
    
    def render(self, ch, pos, shape=None):
        (x,y) = pos
        mch, a1, a2 = self.vneseinfo.decompose(ch)
        a1 = int(a1); a2=int(a2)
        rs = np.zeros(shape, dtype=np.uint8)
        bound, mask = self.mfont.render(mch, pos, rs.shape)
        rs = cv2.bitwise_or(rs, mask)
        newbound = pygame.Rect(bound)
        xa0 = bound.x + bound.width/2
        ya0 = bound.y
        pos1, pos2 = self.mat[ch]
        if pos1 is not None:
            xa1 = xa0 + self.mfont.normHeight() * pos1[0]
            ya1 = ya0 - self.mfont.normHeight() * pos1[1] ### human perception from bottom to top
            if a1 == 5: ya1 += bound.height
            b1, mask1 = self.accent_renderer.render(a1, (xa1, ya1), rs.shape)
            print mask1.shape
            print rs.shape
            rs = cv2.bitwise_or(rs, mask1)
            newbound = None
        if pos2 is not None:
            xa2 = xa0 + self.mfont.normHeight() * pos2[0]
            ya2 = ya0 - self.mfont.normHeight() * pos2[1]### human perception from bottom to top
            if a2 == 5: ya2 += bound.height     
            b2, mask2 = self.accent_renderer.render(a2,  (xa2, ya2), rs.shape)
            rs = cv2.bitwise_or(rs, mask2)
            newbound = None
        return bound, rs
    
    def spaceWidth(self):
        return self.mfont.spaceWidth()
    def normHeight(self):
        return self.mfont.normHeight()

if __name__ == '__main__':
    charset = string.ascii_letters + string.digits
    pf = TTFFont(charset, 40, '/home/loitg/Downloads/fonts/fontss/receipts/general_fairprice/LEFFC2.TTF')
    pf.overWrite('j', None, None, (1.0,1.5))
    af = AccentedFont(pf, '/home/loitg/workspace/genline/resource/fontss/cmnd/chu_in/type_accent2', 
                      '/home/loitg/workspace/clocr/temp/diacritics2.csv')
    
    mat = ( (0.0,0.0),(0.0,0.0))
    af.overWrite(u'ậ', pos = mat)
    for i in range(1,10): af.accent_renderer.overWrite(i, rotation=0.0, scale=(1.0,1.0))
    _, mask = af.render(u'a', (50,50),(100,100))
    cv2.imshow('kk', mask)
    cv2.waitKey(-1)
    
    
    
    
    
    
