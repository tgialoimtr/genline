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

from matplotlib import pyplot as plt
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
        self.renderer2 = TextRenderer('ABCDEFGHIJKLMNOPQRSTUVWXYZ', {'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_den/UTM HelveBold.ttf',
                                                    'base-height':30, 'height':30})        
        self.renderer = TextRenderer('0123456789', {'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/9thyssen.ttf',
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
    
if __name__ == '__main__':
    pipe_id = CMNDPipeID()
    txtgen = RegExGen(r'[0-3]\d{8}')
    a=-0.4; b=0.4; c={}
    for i in range(10):
        if i==1: continue
        c['1'+str(i)] = b
        c[str(i)+'1'] = a
    
    params = {
        'id':
        {
            'font':
            {
                'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/9thyssen.ttf',
                'detail-font':
                    {'4':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/OFFSFOW.ttf'},
                'base-height':33,
                'detail-height':{'4':33},
                'base-ratio':{'x':1.5,'y':1.0},
#                 'detail-ratio':{}
            },
            'relpos':
            {
                'base-relpos-x':0.3,
                'detail-relpos-x': c,
                'relpos-y': {'4':0.3}
            },          
            'x0':57,
            'y0':31,
            'height':33,
            'strength':0.95
        },
        'cmnd':
        {
            'font':
            {
                'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_den/UTM HelveBold.ttf',
                'base-height':30,
                'base-ratio':{'x':1.5,'y':1.0}
            },
            'relpos':
            {
                'base-relpos-x':0.3,
                'relpos-y':{}
            },
            'x0':47,
            'y0':2,
            'strength':0.6,
            'height':30
        },             
        'guiso':
        {
            'strength':0.6,
            'height':20,
            'amp':1,
            'wavelength':40,
            'length':220,
            'angle':0.0,
            'thick':1,
            'x0':144,
            'y0':18            
        },
        'circle':
        {
            'strength':0.6,
            'R1':87,
            'R2':97,
            'a1':2,
            'a2':3,
            'n':90, # number on circles
            'thick':1,
            'x0':76,
            'y0':111
        },
        'height':32,
        'width':'280:300',
        'pad':20,
        'cut':'5:10',
        'strength-bg':0.2,
        'scale':'1.1',
        'rotate':'0',
        'si_blur': {},
        'si_dot': {},
        'si_blob': {}
        
        
        
        
        
        }
    
    pipe_id.p.reset(params)
    
    for i in range(30):
        pipe_id.txt = '272314968' #txtgen.gen()
        mask, mask_chars, txt = pipe_id.gen()
#         mask = cv2.resize(mask, None, fx=0.5, fy=0.5)
#         mask = cv2.resize(mask, None, fx=4.0, fy=4.0)
        hm = gray2heatmap(mask)
        cv2.imshow('mask', mask)
#         cv2.imshow('hm', hm)
#         cv2.imshow('mask0', mask_chars[1])
        cv2.waitKey(-1)
    
    
#     cv2.imshow('mask', mask)
#     for img, bb in zip(charmasks,charbbs):
#         cv2.imshow('mask0', img)
#         aaa = mask[bb[1]:(bb[1]+bb[3]), bb[0]:(bb[0]+bb[2])]
#         cv2.imshow('bb0', aaa)
#         cv2.waitKey(-1)
#     sys.exit(0)