#!/usr/bin/python
# -*- coding: utf8 -*-

'''
Created on Jun 5, 2018

@author: loitg
'''

import cv2
import sys
import random
import numpy as np
from paramatch.params import GenerativeParams, ChangableParams
from shaperender.shape import BGDummyGui, CMNDCircle, BGGuiCMNDSo
from light.shooteffect import ShootEffect
from textrender.textrenderer import TextRenderer
from textrender.font import TTFFont
from textrender.relpos_matrix import RelPos4D
from textgen.items import RegExGen
from light.colorize3_poisson import Layer
from textgen.vnnames import HoTenGen, QuanHuyenGen
from utils.common import no_accent_vietnamese

from matplotlib import pyplot as plt
from src.utils.common import RESOURCE_PATH

def gray2heatmap(img):
    cmap = plt.get_cmap('jet')
    
    rgba_img = cmap(img)
    rgb_img = np.delete(rgba_img, 3, 2)
    return rgb_img

def merge(bg, fg, fg_intensity):
    fg = fg/255.0
    c_r = ((1-fg)*bg)[:,:] + fg[:,:] * fg_intensity
    return c_r

def mergeList(bg, fgs):
    ret = bg if bg is not None else np.zeros_like(fgs[0][0], dtype=float)
    for fg, inten in fgs:
        ret = merge(ret, fg, inten)
    return ret


def hsv2bgr(col_hsv):
    assert len(col_hsv) == 3
    col = cv2.cvtColor(np.array(col_hsv, 'uint8').reshape((1,1,3)), cv2.COLOR_HSV2BGR)
    return col[0,0]


class CMNDPipeID(object):
    '''
    classdocs
    '''

    def __init__(self):
        self.txt = '123'
        self.p = GenerativeParams()
        self.renderer2 = TextRenderer('ABCDEFGHIJKLMNOPQRSTUVWXYZ.', {'base-font':'fontss/cmnd/so_den/UTM HelveBold.ttf',
                                                    'base-height':30, 'height':30})        
        self.renderer = TextRenderer('0123456789', {'base-font':'fontss/cmnd/so_do/9thyssen.ttf',
                                                    'base-height':30, 'height':30})
        self.guiSo = BGGuiCMNDSo()
        self.guiBG = BGDummyGui()
        self.circle = CMNDCircle()
        self.si = ShootEffect()
        
    def renderText(self, renderer, font_dict, relposx_dict, txt, pos, shape, angle, height):
        x0, y0 = pos
        params = {
               'height':height
               }
        renderer.overWrite(**params)
        renderer.overWriteFont(font_dict)
        renderer.overWriteRelPos(relposx_dict)
        mask,b,c = renderer.render((x0, y0), shape, txt)
        return mask,b,c
        
    def gen(self):
        gened = self.p.getChangable()
        id_font_dict = gened['id']['font']
        id_relpos_dict = gened['id']['relpos']
        cmnd_font_dict = gened['cmnd']['font']
        cmnd_relpos_dict = gened['cmnd']['relpos']
        self.height = int(gened['height'] + 2*gened['pad'])
        self.width = int(gened['width'] + 2*gened['pad'])
        
        # build 
        mask_id, mask_char_id, bb_id = self.renderText(self.renderer, id_font_dict, id_relpos_dict, self.txt, 
                                                (gened['id']['x0'],gened['id']['y0']), 
                                                (self.height, self.width),
                                                0,
                                                gened['id']['height'])
        mask_cmnd, _, _ = self.renderText(self.renderer2, cmnd_font_dict, cmnd_relpos_dict, 'CHUNG MINH NHAN DAN', 
                                                (gened['cmnd']['x0'],gened['cmnd']['y0']), 
                                                (self.height, self.width),
                                                0,
                                                gened['cmnd']['height'])
        
        self.guiSo.overWrite(**gened['guiso'])
        mask_guiso = self.guiSo.render((gened['guiso']['x0'],gened['guiso']['y0']), 
                                       (self.height, self.width))
        mask_guibg = self.guiBG.render((None,None), (self.height, self.width))
        
        self.circle.overWrite(**gened['circle'])
        mask_circle = self.circle.render((gened['circle']['x0'],gened['circle']['y0']), 
                                       (self.height, self.width))
        
        fgs = [(mask_guibg, gened['strength-bg']), (mask_guiso, gened['guiso']['strength']),
               (mask_circle, gened['circle']['strength']), (mask_cmnd, gened['cmnd']['strength'])]
        ret0 = (mergeList(None, fgs)*255).astype(int)
        ret0 = self.si.matnet(ret0)
        ret0 = self.si.blur(ret0)      
        mask_id = self.si.matnet(mask_id)
        mask_id = self.si.blur(mask_id)
        ret1 = 1.0-mergeList(ret0/255.0, [(mask_id, gened['id']['strength'])])
        ret1 = self.si.addnoise0(255*ret1)
        ret1 = self.si.heterogeneous0(ret1)
        ret1 = self.si.colorBlob0(ret1)

        
        M = cv2.getRotationMatrix2D((self.width/2,self.height/2),int(gened['rotate']),gened['scale'])
        mask_chars = [cv2.warpAffine(mask, M, (self.width, self.height)) for mask in mask_char_id]
        ret1 = cv2.warpAffine(ret1, M, (self.width, self.height))
        newy0 = int(gened['cut'])
        newx0 = int(gened['cut'])
        mask_chars = [mask[newy0:(newy0+int(gened['height'])), newx0:(newx0+int(gened['width']))] for mask in mask_chars]
        ret1 = ret1[newy0:(newy0+int(gened['height'])), newx0:(newx0+int(gened['width']))]
             
        return ret1, mask_chars, self.txt

class CMNDPipeName(object):
    '''
    classdocs
    '''

    def __init__(self):
        self.txt = 'INSERT NAME'
        self.p = GenerativeParams()
#         self.renderer = TextRenderer('ABCDEFGHIJKLMNOPQRSTUVWXYZ.ẠẢÃÀÁÂẬẦẤẨẪĂẮẰẶẲẴÓÒỌÕỎÔỘỔỖỒỐƠỜỚỢỞỠÉÈẺẸẼÊẾỀỆỂỄÚÙỤỦŨƯỰỮỬỪỨÍÌỊỈĨÝỲỶỴỸĐạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđ', {'base-font':'fontss/cmnd/chu_in/SP3 - Traveling Typewriter.otf',
#                                                     'base-height':30, 'height':30})
        self.renderer = TextRenderer('abcdefghijklmnopqrstuvwxyz:ABCDEFGHIJKLMNOPQRSTUVWXYZ.,-\'r1234567890', {'base-font':'fontss/cmnd/chu_in/SP3 - Traveling Typewriter.otf',
                                                    'base-height':30, 'height':30},
                                      accent_dir= RESOURCE_PATH + 'fontss/cmnd/chu_in/type_accent2',
                                      vninfo_dir= RESOURCE_PATH + 'diacritics2.csv') 
        self.guiBG = BGDummyGui()
        self.circle = CMNDCircle()
        self.si = ShootEffect()
        
    def renderText(self, renderer, font_dict, relposx_dict, txt, pos, shape, angle, height, accent_info=None, accent_relpos=None):
        x0, y0 = pos
        params = {
               'height':height
               }
        renderer.overWrite(**params)
        renderer.overWriteFont(font_dict)
        renderer.overWriteRelPos(relposx_dict)
        if accent_info is not None: renderer.overWriteAccent(accent_info)
        if accent_relpos is not None: renderer.overWriteRelPosAccent(accent_relpos)
        mask,b,c = renderer.render((x0, y0), shape, txt)
        return mask,b,c
    
    def gen(self):
        gened = self.p.getChangable()
        name_font_dict = gened['name']['font']
        name_relpos_dict = gened['name']['relpos']
        dots_font_dict = gened['dots']['font']
        dots_relpos_dict = gened['dots']['relpos']
        self.height = int(gened['height'] + 2*gened['pad'])
        self.width = int(gened['width'] + 2*gened['pad'])
        
        # build 
        mask_name, mask_char_name, bb_name = self.renderText(self.renderer, name_font_dict, name_relpos_dict, self.txt, 
                                                (gened['name']['x0'],gened['name']['y0']), 
                                                (self.height, self.width),
                                                0,
                                                gened['name']['height'],
                                                accent_info=gened['name']['accent-info'],
                                                accent_relpos=gened['name']['accent-relpos'])
        mask_dots, mask_char_dots, _ = self.renderText(self.renderer, dots_font_dict, dots_relpos_dict,'n:' + '.'*80, 
                                                (gened['dots']['x0'],gened['dots']['y0']), 
                                                (self.height, self.width),
                                                0,
                                                gened['dots']['height'])
        
        #self.guiSo.overWrite(**gened['guiso'])
        #mask_guiso = self.guiSo.render((gened['guiso']['x0'],gened['guiso']['y0']), 
        #                               (self.height, self.width))
        mask_guibg = self.guiBG.render((None,None), (self.height, self.width))
        
        self.circle.overWrite(**gened['circle'])
        mask_circle = self.circle.render((gened['circle']['x0'],gened['circle']['y0']), 
                                       (self.height, self.width))
        
        fgs = [(mask_guibg, gened['strength-bg']), (mask_circle, gened['circle']['strength'])]
        ret0 = (mergeList(None, fgs)*255).astype(int)
        ret0 = self.si.matnet(ret0)
        ret0 = self.si.blur(ret0, (1,1))    
        mask_name = self.si.inkeffect(mask_name) 
#         mask_name = self.si.matnet(mask_name)
        mask_name = self.si.blur(mask_name, (1,1))
        mask_dots = self.si.blur(mask_dots, (1,1))
        ret1 = 1.0-mergeList(ret0/255.0, [(mask_dots, gened['dots']['strength']), (mask_name, gened['name']['strength'])])
        ret1 = self.si.addnoise0(255*ret1, 10)
        ret1 = self.si.heterogeneous0(ret1)
        ret1 = self.si.colorBlob0(ret1)
        ret1 = self.si.distort(ret1)

        
        M = cv2.getRotationMatrix2D((self.width/2,self.height/2),int(gened['rotate']),gened['scale'])
        mask_chars = [cv2.warpAffine(mask, M, (self.width, self.height)) for mask in mask_char_name]
        ret1 = cv2.warpAffine(ret1, M, (self.width, self.height))
        newy0 = int(gened['cut'])
        newx0 = int(gened['cut'])
        mask_chars = [mask[newy0:(newy0+int(gened['height'])), newx0:(newx0+int(gened['width']))] for mask in mask_chars]
        ret1 = ret1[newy0:(newy0+int(gened['height'])), newx0:(newx0+int(gened['width']))]
             
        return ret1, mask_chars, self.txt
        
if __name__ == '__main__':
#     pipe_id = CMNDPipeID()
#     txtgen = RegExGen(r'[0-3]\d{8}')
#     a=-0.4; b=0.4; c={}
#     for i in range(10):
#         if i==1: continue
#         c['1'+str(i)] = b
#         c[str(i)+'1'] = a
#     
#     paramsID = {
#         'id':
#         {
#             'font':
#             {
#                 'base-font':'fontss/cmnd/so_do/9thyssen.ttf',
#                 'detail-font':
#                     {'4':'fontss/cmnd/so_do/OFFSFOW.ttf'},
#                 'base-height':33,
#                 'detail-height':{'4':33},
#                 'base-ratio':{'x':'1.20:1.40','y':1.0},
# #                 'detail-ratio':{}
#             },
#             'relpos':
#             {
#                 'base-relpos-x':0.25,
#                 'detail-relpos-x': c,
#                 'relpos-y': {'4':'0.10:0.15'}
#             },          
#             'x0':'65+-5',
#             'y0':'60+-3',
#             'height':37,
#             'strength':'0.95:1.00'
#         },
#         'cmnd':
#         {
#             'font':
#             {
#                 'base-font':'fontss/cmnd/so_den/UTM HelveBold.ttf',
#                 'base-height':30,
#                 'base-ratio':{'x':1.0,'y':1.0}
#             },
#             'relpos':
#             {
#                 'base-relpos-x':0.05,
#                 'relpos-y':{}
#             },
#             'x0':35,
#             'y0':25,
#             'strength':0.6,
#             'height':25
#         },             
#         'guiso':
#         {
#             'strength':'0.60:0.80',
#             'height':25,
#             'amp':1,
#             'wavelength':40,
#             'length':280,
#             'angle':'-0.5:0.5',
#             'thick':1,
#             'x0':185,
#             'y0':50           
#         },
#         'circle':
#         {
#             'strength':'0.60:0.80',
#             'R1':'92+-3',
#             'R2':'102+-3',
#             'a1':2,
#             'a2':3,
#             'n':90, # number on circles
#             'thick':1,
#             'x0':66,
#             'y0':136
#         },
#         'height':64,
#         'width':'350+-10',
#         'pad':20,
#         'cut':'15:20',
#         'strength-bg':'0.2+-0.05',
#         'scale':'1.00:1.20',
#         'rotate':'0.0:1.5',
#         'si_blur': {},
#         'si_dot': {},
#         'si_blob': {}
#         }
#     
#     pipe_id.p.reset(paramsID)
#     pipe_id.txt = '024540261' #txtgen.gen()
#     mask, mask_chars, txt = pipe_id.gen()
# #    cv2.imshow('mask', mask)
#     cv2.imwrite("test.jpg",mask)
#     
#     
# #     cv2.imshow('mask', mask)
# #     for img, bb in zip(charmasks,charbbs):
# #         cv2.imshow('mask0', img)
# #         aaa = mask[bb[1]:(bb[1]+bb[3]), bb[0]:(bb[0]+bb[2])]
# #         cv2.imshow('bb0', aaa)
# #         cv2.waitKey(-1)
# #     sys.exit(0)


    paramsName = {
        'name':
        {
            'font':
            {
                'base-font':'fontss/cmnd/chu_in/SP3 - Traveling Typewriter.otf',
                'base-height':33,
                'base-ratio':{'x':1.1,'y':1.0},
            },
            'relpos':
            {
                'base-relpos-x':0.03,
                
                
            },
            'accent-relpos': 
            {
                'rel-accent':
                {
                    '61':{'x':0.0,'y':0.0},
                    '62':{'x':0.0,'y':0.0},
                    '63':{'x':0.0,'y':0.0},
                    '64':{'x':0.0,'y':0.1},
                    '81':{'x':0.0,'y':0.0},
                    '82':{'x':0.0,'y':0.0},
                    '83':{'x':0.0,'y':0.0},
                    '84':{'x':0.0,'y':0.0},
                },
                'rel-char':
                {
                    'default':{'x':-0.2,'y':0.2},
                    '61':{'x':0.0,'y':0.0},
                    '62':{'x':0.0,'y':0.0},
                    '63':{'x':0.0,'y':0.0},
                    '64':{'x':0.0,'y':0.3},
                    '81':{'x':0.0,'y':0.0},
                    '82':{'x':0.0,'y':0.0},
                    '83':{'x':0.0,'y':0.0},
                    '84':{'x':0.0,'y':0.0},
                    '5':{'x':0.0,'y':-0.5},
                }
             },
            'accent-info':
            {
                '1':{'default-height':10},
               '2':{'default-height':10},
               '3':{'default-height':10},
               '4':{'default-height':10},
               '5':{'default-height':10},
               '6':{'default-height':10},
               '7':{'default-height':10},
               '8':{'default-height':10},
               '9':{'default-height':10}
            },
            'x0':80,
            'y0':65,
            'height':40,
            'strength':0.95
        },
        'dots':
        {
            'font':
            {
                'base-font':'fontss/cmnd/so_den/UTM HelveBold.ttf',
                'base-height':30,
                'base-ratio':{'x':1.0,'y':1.0}
            },
            'relpos':
            {
                'base-relpos-x':0.15,
                'relpos-y':{}
            },
            'x0':40,
            'y0':75,
            'strength':1,
            'height':10
        },             
        'guiso':
        {
            'strength':'0.60:0.80',
            'height':20,
            'amp':1,
            'wavelength':40,
            'length':'320:340',
            'angle':0.0,
            'thick':1,
            'x0':200,
            'y0':18            
        },
        'circle':
        {
            'strength':'0.6+-0.05',
            'R1':'87+-3',
            'R2':'102+-3',
            'a1':2,
            'a2':3,
            'n':90, # number on circles
            'thick':1,
            'x0':155,
            'y0':120
        },
        'circle2':
        {
            'strength':'0.5+-0.05',
            'R1':'125+-3',
            'R2':'145+-3',
            'a1':2,
            'a2':3,
            'n':90, # number on circles
            'thick':1,
            'x0':155,
            'y0':120
        },
        'height':64,
        'width':640,
        'pad':20,
        'cut':'15:20',
        'strength-bg':'0.2+-0.05',
        'scale':'1.00:1.20',
        'rotate':'0.0:1.5',
        'si_blur': {},
        'si_dot': {},
        'si_blob': {}
        
        }
    
    pipe_name = CMNDPipeName()
    pipe_name.p.reset(paramsName)
    gener = HoTenGen(RESOURCE_PATH + 'hovaten.csv')
    pipe_name.txt = u'NGUYỄN THỊ THU THẢO'#u'TRƯƠNG GIA LỢI'
    #pipe_name.txt = gener.gen()
    mask, mask_chars, txt = pipe_name.gen()
    cv2.imshow('fdf', mask)
    cv2.waitKey(-1)
    #cv2.imwrite("/tmp/test/testName.jpg",mask)
    #for i in range(len(mask_chars)):
    #    cv2.imwrite("/tmp/test/testName"+str(i)+".jpg",mask_chars[i])
    #    print(i)
    #print(txt)
    #cv2.waitKey(0)







