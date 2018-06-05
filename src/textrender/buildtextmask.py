'''
Created on Jan 24, 2018

@author: loitg
'''
import os, sys
from numpy import average
from clgen import receiptgenline
# Config PYTHONPATH and template folder relatively according to current file location
project_dir = os.path.dirname(__file__) + '/../'
sys.path.insert(0, project_dir)
# from synthgen import *
import cv2
import numpy as np
import pygame
from pygame import freetype
from text_utils import RenderFont
import rstr
from clgen.receiptgenline import CapitalandGen
from textgen.combiner import ListGenWithProb
import re, random


DATA_PATH = '/home/loitg/workspace/genreceipt/resource/'
FONT_PATH = '/home/loitg/Downloads/fonts/fontss/'
fontlist = ['general_fairprice/PRINTF Regular.ttf', #chi so x0.85 (chux0.65-0.75)
             #'general_fairprice/Instruction.otf',
             #'general_fairprice/Instruction Bold.otf',
             'general_fairprice/LEFFC___.TTF', #chi chu x1.3-5 (x0.85)
             'general_fairprice/LEFFC2.TTF', #chi chu x1.3-5 (x0.85)
#              'general_fairprice/LiberationMono-Regular.ttf',
             'general_fairprice/Merchant Copy.ttf', #x0.8-9- (x1.15-) (x0.72)
#              'general_fairprice/Merchant Copy Wide.ttf',
#              'general_fairprice/Monaco.ttf',
#              'general_fairprice/typewcond_regular.otf',
#              'general_fairprice/typewcond_demi.otf',
#              'general_fairprice/saxmono.ttf',
#              'bedok/Galeries.ttf', 
#             'dotted/5by7_b.ttf',
#             'dotted/DOTMATRI.TTF',
#             'dotted/5by7.ttf',
            'dotted/fake receipt.ttf', # dung duoc (x0.65) (0.5) (0.8)
            'dotted/jd_lcd_rounded.ttf', # dung duoc x0.95 (x0.65) (0.8)
#             'dotted/epson1.ttf',
#             'westgate/PetMe1282Y.ttf',
#             'westgate/PetMe128.ttf',
#             'westgate/PetMe64.ttf',
            'westgate/PKMN-Mystery-Dungeon.ttf', # chi chu va so (NOT SYMBOL)
#             'westgate/PetMe.ttf',
#             'westgate/PetMe642Y.ttf',
#             'westgate/PetMe2X.ttf',
            'westgate/PetMe2Y.ttf', #dung duoc x1.43 (x0.8) x1.2
            'westgate/karmasut.ttf', # dung duoc (x0.75)
#             'westgate/SYDTWO_2.ttf',
             ]

def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
 
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
 
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
 
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
 
    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))

class AFont(object):
    
    def __init__(self, fontpath, p, w2h, s2h, size=100):
        self.prob = p
        self.fontpath = fontpath
        self.font = freetype.Font(fontpath, size=size)
        self.w2h = w2h # tuple (rangemin, rangemax)
        self.s2h = s2h # tuple (rangemin, rangemax)
        self.font.underline = False
        self.font.strong = False
        self.font.oblique = False
        self.font.strength = False
        self.font.antialiased = True
        self.font.origin = True
    
    def getFont(self):
        return self.font    

    def isIn(self, queries):
        name = self.fontpath.split('/', 1)[1].lower()
        for query in queries:
            if query.lower() in name:
                return True
        return False

class LoitgFont(object):
    
    def __init__(self, fontpath, p, widthrange, size=100):
        self.prob = p
        self.fontpath = fontpath
        self.font = freetype.Font(fontpath, size=size)
        self.widthrange = widthrange
        self.font.underline = False
        self.font.strong = False
        self.font.oblique = False
        self.font.strength = False
        self.font.antialiased = True
        self.font.origin = True
        
    def getFont(self):
        return self.font
    
    def getRatio(self):
        return (self.widthrange[1] - self.widthrange[0])*np.random.sample() + self.widthrange[0]

class Fonts(object):
    allfonts = {}
    def __init__(self, afonts):
        self.fonts = []
        probs = []
        for p, fontname, w2h, s2h in afonts:
            font = AFont(FONT_PATH+fontname, p, w2h, s2h)
            self.allfonts[FONT_PATH+fontname] = font
            self.fonts.append(font)
            probs.append(p)
        self.fontgen = ListGenWithProb(self.fonts, probs)
        
    def genRandom(self):
        return self.fontgen.gen()
    
    def genByName(self, query):
        rs = []
        for name, font in self.allfonts.iteritems():
            name = name.split('/')[-1]
            if query.lower() in name.lower():
                rs.append(font)
        if len(rs) == 1:
            return rs[0]
        else:
            return None
        
    
class RenderText(object):
    def __init__(self, afonts=[]):
        pygame.init()
        self.renderfont = RenderFont(DATA_PATH)
        self.height = 100
        self.pad_for_cut = 10
        self.rel_line_spacing = 1.0
        self.loitgfonts = []
        self.fonts = []
        probs = []
        for p, fontname, w2h, s2h in afonts:
            self.fonts.append(AFont(FONT_PATH+fontname, p, w2h, s2h))
            probs.append(p)
        if len(self.fonts) > 0: self.fontgen = ListGenWithProb(self.fonts, probs)

    def init_font(self, fontpath, spacing):
        font = freetype.Font(FONT_PATH + fontpath, size=self.height)
        font.underline = False
        font.strong = False
        font.oblique = False
        font.strength = False
        font.antialiased = True
        font.origin = True
        self.spacing = spacing
        return font    
    
    def genFont(self):
        if len(self.fonts) > 0:
            return self.fontgen.gen()
        else:
            return None
    
    def toMask2(self, afont, txt):
        ###
        s2h = random.uniform(afont.s2h[0], afont.s2h[1])
        w2h = random.uniform(afont.w2h[0], afont.w2h[1])
        ###
        
        txt_arr, _, bbs = self.renderfont.render_singleline(afont.font, txt , w2h, s2h)
        newwidth = int(txt_arr.shape[1]*w2h)
        txt_arr = cv2.resize(txt_arr,(newwidth, txt_arr.shape[0]))
        return txt_arr, txt
    
    def toMask(self, loitgfont, txt, otherlines=False):
        if loitgfont.fontpath == '/home/loitg/Downloads/fonts/fontss/receipts/westgate/PKMN-Mystery-Dungeon.ttf' and any(c in txt for c in ['<','>',';','!','$','#','&','/','`','~','@','%','^','*','.']):
            return None, None
        if loitgfont.fontpath == '/home/loitg/Downloads/fonts/fontss/receipts/general_fairprice/LEFFC2.TTF' and any(c.isdigit() for c in txt):
            return None, None
        if (loitgfont.fontpath == '/home/loitg/Downloads/fonts/fontss/receipts/general_fairprice/PRINTF Regular.ttf')\
             or (loitgfont.fontpath == '/home/loitg/Downloads/fonts/fontss/receipts/dotted/fake receipt.ttf'):
            txt = txt.upper()
        above = rstr.rstr('ABC0123456789abcdef ', len(txt))
        below = rstr.rstr('ABC0123456789abcdef ', len(txt))
        multilines = above + '\n' + txt + '\n' + below
        if otherlines:
            txt_arr, _, bbs = self.renderfont.render_multiline(loitgfont.font, multilines , 0.3, 0.2, 1)
#             angle = np.random.rand() * 3 + 3
#             if np.random.rand() < 0.5: angle = -angle
#             txt_arr= rotate_bound(txt_arr,angle)
        else:
            txt_arr, _, bbs = self.renderfont.render_multiline(loitgfont.font, multilines , 0.05, 0.5, 1)
#             angle = np.random.randn() * 2
#             if np.random.rand() < 0.5 and abs(angle) > 1 and abs(angle) < 10:
#                 txt_arr= rotate_bound(txt_arr,angle)

        angle = np.random.randn() * 3
        if np.random.rand() < 0.4:
            txt_arr= rotate_bound(txt_arr,angle)            
        
        newwidth = int(txt_arr.shape[1]*loitgfont.getRatio())
        if np.random.rand() < 0.4:
            found = re.search( r'\d\.\d\d', txt)
            if found:
                newwidth *= 2
            elif any(c in txt for c in receiptgenline.TOTAL_KEYS) or \
                any(c.upper() in txt for c in receiptgenline.TOTAL_KEYS):
                newwidth *= 2
        txt_arr = cv2.resize(txt_arr,(newwidth, txt_arr.shape[0]))
        return txt_arr, txt
 
if __name__ == '__main__':
#     p, path, r0, r1 = loitgfonts[6]
#     render = RenderText()
#     lf = LoitgFont(FONT_PATH+path, p, (r0, r1),size=40)
#     txt = ';:\'\",.<>/?'
#     txt='`~!@#$%^&*()-=_+'
#     txt='[]{}\|'
#     txt = [x for x in txt]
#     txt = '\n'.join(txt)
#     print txt
#     txt_arr, txt, bbs = render.renderfont.render_multiline(lf.font, txt , 10, 0.1, -1)
#     cv2.imshow('m', txt_arr)
#     cv2.waitKey(-1)
#     
#     exit(0)
    
    
    
    
    render = RenderText()
    clgen = CapitalandGen()
    
#    fontpath = fontslist[int(np.random.randint(0, len(fontslist)))]
    for _ in range(300):
        loitgfont = render.genFont()
        txt = clgen.gen()
        print loitgfont.fontpath
        m = render.toMask(loitgfont, txt=txt, otherlines = True)
        if m is None: continue
        cv2.imshow('m', m)
        cv2.waitKey(-1)
        
    

        
    
