'''
Created on Jun 5, 2018

@author: loitg
'''
import cv2
import sys
import random
import numpy as np
from paramatch.params import Params
from textrender.textrenderer import RelPosRenderer
from textrender.font import TTFFont
from textrender.relpos_matrix import RelPos4D
from textgen.items import RegExGen
from light.colorize3_poisson import Layer



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
        self.p = Params()        
        
        ### FONTS
        self.charset = '0123456789'
        basefont = '/home/loitg/Downloads/fonts/fontss/receipts/general_fairprice/LEFFC2.TTF'
        self.charfont = TTFFont(self.charset, 40, basefont)
        ### RelPos
        self.mat = RelPos4D(self.charset)
        self.mat.mat[('a','b')].hor = -0.1
        self.mat.mat[('1','2')].hor = +0.5
        
        
        self.renderer = RelPosRenderer(self.charset, self.charfont)
    

    
    
    def buildCommonParams(self):
        bg_col_hsv = (random.randint(122,220)*180/360, random.randint(1,16)*255/100, random.randint(70,100)*255/100)
        guilloche_col_hsv = (random.randint(122,190)*180/360, random.randint(10,40)*255/100, random.randint(30,90)*255/100)
        while guilloche_col_hsv[1] < bg_col_hsv[1] or guilloche_col_hsv[2] > bg_col_hsv[2]:
            guilloche_col_hsv = (random.randint(122,190)*180/360, random.randint(10,40)*255/100, random.randint(30,90)*255/100)
#         guilloche_col_hsv = (bg_col_hsv[0], bg_col_hsv[1] + random.randint(0,10), bg_col_hsv[2] + random.randint(-20,-5))
        text_col_hsv = (bg_col_hsv[0], bg_col_hsv[1]*random.uniform(1.3,2.2), bg_col_hsv[2]/random.uniform(1.5,2.5))
        sodo_col_hsv = (random.randint(330,350)*180/360, random.randint(25, 47)*255/100, random.randint(45,75)*255/100)
        self.bg_col = hsv2bgr(bg_col_hsv)
        self.guilloche_col = hsv2bgr(guilloche_col_hsv)
        self.text_col = (random.randint(2,69), random.randint(2,69), random.randint(2,69)) #hsv2bgr(text_col_hsv)
        self.sodo_col = hsv2bgr(sodo_col_hsv) 
        self.x0 = self.p.new('center_x_id', self.width/2, paramrange=(0, self.width), freeze=True).x
        self.y0 = self.p.new('center_y_id', self.height/2, paramrange=(0, self.height), freeze=True).x    

    def buildId(self):
        #(self, txt, shape, ybaseline, height, x0, relposmat=None, relposmat2=None):   
        mask, charmasks, charbbs = self.renderer.render(self.txt, (self.height, self.width), 40, 100, 20, self.mat)
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
    "rel-width" : {"a": "1.2+-0.1", "b":"0.3-0.6" }, 
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