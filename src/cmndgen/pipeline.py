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

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.txt = '123'
        self.p = GenerativeParams()
        
        self.renderer = TextRenderer('0123456789', {'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/9thyssen.ttf',
                                                    'base-height':30, 'height':30})
        self.guiSo = BGGuiCMNDSo()
        self.guiBG = BGDummyGui()
        self.circle = CMNDCircle()
        self.si = ShootEffect()
        
    def buildId(self, font_dict, relposx_dict, txt, (x0,y0), shape, angle, height):
        params = {
               'height':height
               }
        self.renderer.overWrite(**params)
        self.renderer.overWriteFont(font_dict)
        self.renderer.overWriteRelPosX(relposx_dict)
        mask,b,c = self.renderer.render((x0, y0), shape, txt)
        return mask,b,c
        
    def gen(self):
        gened = self.p.getChangable()
        id_font_dict = gened['id']['font']
        id_relpos_dict = gened['id']['relpos']
#         cmnd_font_dict = gened['cmnd_font']
#         cmnd_relpos_dict = gened['cmnd_relpos']
        
        # build 
        mask_id, mask_char_id, bb_id = self.buildId(id_font_dict, id_relpos_dict, self.txt, 
                                                (gened['id']['x0'],gened['id']['y0']), 
                                                (self.height, self.width),
                                                0,
                                                gened['id']['height'])
#         mask_cmnd,_,_ = self.buildCmnd()
        
        self.guiSo.overWrite(**gened['guiso'])
        mask_guiso = self.guiSo.render((gened['guiso']['x0'],gened['guiso']['y0']), 
                                       (self.height, self.width))
        mask_guibg = self.guiBG.render((None,None), (self.height, self.width))
        
        self.circle.overWrite(**gened['circle'])
        mask_circle = self.circle.render((gened['circle']['x0'],gened['circle']['y0']), 
                                       (self.height, self.width))
        
        fgs = [(mask_guibg, 0.1), (mask_guiso, 0.4), (mask_circle, 0.6)]
        ret0 = (mergeList(None, fgs)*255).astype(int)
        ret0 = self.si.matnet(ret0)
        ret0 = self.si.blur(ret0)      
        mask_id = self.si.matnet(mask_id)
        mask_id = self.si.blur(mask_id) 
        mask_id = self.si.sonhoe(mask_id)
        ret1 = 1.0-mergeList(ret0/255.0, [(mask_id, 0.96)])
        ret1 = self.si.addnoise0(255*ret1)
        ret1 = self.si.heterogeneous0(ret1)
        ret1 = self.si.colorBlob0(ret1)        
        return ret1
        
        
#         # LAYERS
#         lGuiBgSo = self.buildGuillocheBGSo()
#         lGuiBG = self.buildGuillocheBG()
#         lId = self.buildId()
#         l_bg = Layer(alpha=255*np.ones((self.height, self.width),'uint8'), color=self.bg_col)
#         ### EFFECTS
#         lGuiBG.alpha = random.uniform(0.4,0.9) * lGuiBG.alpha
#         lId.alpha = self.si.inkeffect(lId.alpha)
#         lId.alpha = self.si.matnet(lId.alpha)
#         lId.alpha = self.si.sonhoe(lId.alpha)
#         lId.alpha = self.si.blur(lId.alpha)
#         lGuiBgSo.alpha = self.si.matnet(lGuiBgSo.alpha)
#         lGuiBgSo.alpha = self.si.blur(lGuiBgSo.alpha)
#         ### MERGES
#         layers = [lId, lGuiBgSo, lGuiBG, l_bg]
#         blends = ['normal'] * len(layers)
#         idline = self.colorize.merge_down(layers, blends).color
#         idline = self.si.addnoise(idline)
#         idline = self.si.heterogeneous(idline)
#         idline = self.si.colorBlob(idline)
#         return idline, txt
    
# if __name__ == '__main__':
#     pipe_id = CMNDPipeID()
#     # Imagine user input -- USING JSON STRING
#     pipe_id.p.reset('')
#     pipe_id.p.reset('', key = 'font') # only effect partial params
#     
#     # Imagine user input -- USING PARAM ASSIGNMENT
#     pipe_id.txt = '024540261'
#     pipe_id.p['height'] = 40
#     pipe_id.p['mat-base'] = 20
#     pipe_id.p['mat-a-b'] = 1.3
#     
#     # 
#     pipe_id.gen()
#     
#     line_param_jsonStr = pipe_id.p.represent() # return single value
#     line_param_csv = flatten(line_param_jsonStr)
#     
#     line_genparam = ''
#     line_genparam = makeDistributor([line_param_jsonStr1, line_param_jsonStr2, ...])
    
if __name__ == '__main__':
    pipe_id = CMNDPipeID(65, 450)
    txtgen = RegExGen(r'[0-3]\d{8}')
    
    params = {
        'id':
        {
            'font':
            {
                'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/9thyssen.ttf',
                'detail-font':
                    {'4':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/OFFSFOW.ttf'},
                'base-height':70,
                'detail-height':{'4':80}
            },
            'relpos':
            {
                'base-relpos':0.3,
                'detail-relpos': {'01':0.9,'12':0.9,'67':-0.5}
            },
            'x0':30,
            'y0':55,
            'height':70
        },
        'cmnd':
        {
            'font':
            {
                'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/9thyssen.ttf',
                'detail-font':
                    {'4':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/OFFSFOW.ttf'},
                'base-height':30,
                'detail-height':{'4':80}
            },
            'relpos':
            {
                'base-relpos':0.3,
                'detail-relpos': {'01':0.9,'12':0.9,'67':-0.5}
            },
            'x0':20,
            'y0':20,
            'height':40
        },             
        'guiso':
        {
            'height':35,
            'amp':3,
            'wavelength':90,
            'length':500,
            'angle':0.0,
            'thick':1,
            'x0':200,
            'y0':30            
        },
        'circle':
        {
            'R1':251,
            'R2':268,
            'a1':2,
            'a2':3,
            'n':120, # number on circles
            'thick':1,
            'x0':60,
            'y0':290
        },
        'scale':1.3,
        'rotate':5,
        'si_blur': {},
        'si_dot': {},
        'si_blob': {}
        
        
        
        
        
        }
    
    pipe_id.p.reset(params)
    
    for i in range(30):
        pipe_id.txt = '272311968' #txtgen.gen()
        mask = pipe_id.gen()
        mask = cv2.resize(mask, None, fx=2.0, fy=2.0)
        hm = gray2heatmap(mask)
        cv2.imshow('mask', mask)
        cv2.imshow('hm', hm)
        cv2.waitKey(-1)
    
    
#     cv2.imshow('mask', mask)
#     for img, bb in zip(charmasks,charbbs):
#         cv2.imshow('mask0', img)
#         aaa = mask[bb[1]:(bb[1]+bb[3]), bb[0]:(bb[0]+bb[2])]
#         cv2.imshow('bb0', aaa)
#         cv2.waitKey(-1)
#     sys.exit(0)