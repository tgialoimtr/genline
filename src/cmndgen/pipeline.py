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
from textrender.textrenderer import TextRenderer
from textrender.font import TTFFont
from textrender.relpos_matrix import RelPos4D
from textgen.items import RegExGen
from light.colorize3_poisson import Layer

def merge(bg, fg, fg_intensity):
    c_r = ((1-fg)*bg)[:,:] + fg[:,:] * fg_intensity
    return c_r

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
                                                    'base-height':30})
        
        
    def buildId(self):
        params = {'txt':'123',
               'relpos-y':{},
               'angle':0.0,
               'height':30
               }
        self.renderer.overWrite(params)
        font_dict = {'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/9thyssen.ttf',
                       'detail-font':{'4':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/OFFSFOW.ttf',
                                     },
                       'base-height':30,
                       'detail-height':{'4':80}
                       }
        self.renderer.overWriteFont(font_dict)
        relposx_dict = {'base-relpos':0.3,
                          'detail-relpos': {'01':0.9,'12':0.9,'67':-0.5}
                          }
        self.renderer.overWriteRelPosX(relposx_dict)
        mask,_,_ = self.renderer.render((0, 50), (100,300), '01234567')
        return Layer(alpha=mask, color=self.sodo_col)
        
    def applyParams(self):
        self.renderer.a = self.p['a'].x
        self.charfont.setFont(self.p['font'].x)
        
        
    def gen(self):
        self.applyParams()
        # LAYERS
        lGuiBgSo = self.buildGuillocheBGSo()
        lGuiBG = self.buildGuillocheBG()
        lId = self.buildId()
        l_bg = Layer(alpha=255*np.ones((self.height, self.width),'uint8'), color=self.bg_col)
        ### EFFECTS
        lGuiBG.alpha = random.uniform(0.4,0.9) * lGuiBG.alpha
        lId.alpha = self.si.inkeffect(lId.alpha)
        lId.alpha = self.si.matnet(lId.alpha)
        lId.alpha = self.si.sonhoe(lId.alpha)
        lId.alpha = self.si.blur(lId.alpha)
        lGuiBgSo.alpha = self.si.matnet(lGuiBgSo.alpha)
        lGuiBgSo.alpha = self.si.blur(lGuiBgSo.alpha)
        ### MERGES
        layers = [lId, lGuiBgSo, lGuiBG, l_bg]
        blends = ['normal'] * len(layers)
        idline = self.colorize.merge_down(layers, blends).color
        idline = self.si.addnoise(idline)
        idline = self.si.heterogeneous(idline)
        idline = self.si.colorBlob(idline)
        return idline, txt
    
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
    pipe_id = CMNDPipeID(80, 608)
    txtgen = RegExGen(r'[0-3]\d{8}')
    pipe_id.p.reset(''' {
    "mat-base":"0.7",
    "rel-width" : {"a": "1.2+-0.1", "b":"0.3:0.6" }, 
    "rel-pos-x" : {"ab": 0.01, "VA": -0.03},
    "rel-pos-y" : {"n":0.07}
    
    } ''')
    
    for i in range(10):
        pipe_id.txt = txtgen.gen()
        pipe_id.gen()
    
    
    
    cv2.imshow('mask', mask)
    for img, bb in zip(charmasks,charbbs):
        cv2.imshow('mask0', img)
        aaa = mask[bb[1]:(bb[1]+bb[3]), bb[0]:(bb[0]+bb[2])]
        cv2.imshow('bb0', aaa)
        cv2.waitKey(-1)
    sys.exit(0)