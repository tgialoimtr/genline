# -*- coding: utf-8 -*-
'''
Created on Mar 17, 2018

@author: loitg
'''
import numpy as np
import pandas as pd
import cv2, rstr
from TextRender.buildtextmask import RenderText, Fonts
from utils.params import cmndconfig
from LightAndShoot.shooteffect import ShootEffect
from LightAndShoot.colorize3_poisson import Layer, Colorize
from TextRender.buildtextmask import rotate_bound
import math, random
from genline.items import RegExGen
from genline.detailgen import DateGen
from ParametersMatching.collections import Params
from genline.combiner import LambdaGen, ListGenWithProb, ComplexGen, PairGen
import re
import unicodedata
from PyQt4.Qt import QHBoxLayout


def no_accent_vietnamese(s):
#     s = s.decode('utf-8')
    s = re.sub(u'Đ', 'D', s)
    s = re.sub(u'đ', 'd', s)
    return unicodedata.normalize('NFKD', unicode(s)).encode('ASCII', 'ignore')


def createTextMask(gener, render, si):
    txt = gener.gen()
    m, txt = render.toMask(render.genFont(), txt=txt, otherlines = True)
    return m, txt

def createSample(gener, render, si):
    textmask, txt = createTextMask(gener, render, si)
    if textmask is None:
        return None, None
    newwidth = int(32.0/textmask.shape[0]*textmask.shape[1])
    textmask = cv2.resize(textmask,(newwidth, 32))
    rs = si.effect(textmask)
    return rs, txt
def hsv2bgr(col_hsv):
    assert len(col_hsv) == 3
    col = cv2.cvtColor(np.array(col_hsv, 'uint8').reshape((1,1,3)), cv2.COLOR_HSV2BGR)
    return col[0,0]

def bgr2hsv(col_hsv):
    assert len(col_hsv) == 3
    col = cv2.cvtColor(np.array(col_hsv, 'uint8').reshape((1,1,3)), cv2.COLOR_BGR2HSV)
    return col[0,0]

def quan(qh):
    rs = qh
    space = u' ' if np.random.rand() < 0.5 else u''
    if np.random.rand() < 0.7:
        rs = rs.replace(u'Quận ', u'Q.'+space) if np.random.rand() < 0.5  else rs.replace(u'Quận ', u'')
        rs = rs.replace(u'Huyện ', u'H.'+space) if np.random.rand() < 0.5  else rs.replace(u'Huyện ', u'')
        rs = rs.replace(u'Thi xã ', u'TX.'+space) if np.random.rand() < 0.5  else rs.replace(u'Thi xã ', u'')
        rs = rs.replace(u'Thành phố ', u'TP.'+space) if np.random.rand() < 0.5  else rs.replace(u'Thành phố ', u'')
    return rs
def tinh(tt):
    rs = tt
    space = u' ' if np.random.rand() < 0.5 else u''
    if np.random.rand() < 0.7:
        rs = rs.replace(u'Thành phố ', u'TP.'+space) if np.random.rand() < 0.5  else rs.replace(u'Thành phố ', u'')
        rs = rs.replace(u'Tỉnh'+space, u'')
    return rs    
    
class Stack:
    
    def __init__(self, width, height, params):
        self.colorize = Colorize()
        self.si = ShootEffect()
        self.renderer = RenderText()
        self.idnumbergen = RegExGen(r'[0-3]\d{8}')
        self.dobgen = DateGen(fromdate='1940-01-01', todate='1999-12-31', dateformat=cmndconfig.date)
        self.p = params

        self.valuefonts = Fonts(cmndconfig.fontvalues)
        self.keyfonts = Fonts(cmndconfig.fontkeys)
        self.idfonts = Fonts(cmndconfig.fontid)
        
        self.width = width
        self.height = height
        self.fullnames = None

    @staticmethod
    def sineWave(x0, y0, length, amp, wavelength, angle=0, phase=0):
        x = np.arange(x0 - length/2, x0 + length/2, 2)
        B = np.array(x, 'float')
        o = np.ones_like(B, float)
        for i, xx in enumerate(x):
            B[i] = math.sin(2.0*math.pi*(xx-x[0])/wavelength + phase)
        B *= amp
        B += y0
        datapoints = np.vstack((x,B,o))
        rotM = cv2.getRotationMatrix2D((x0,y0),angle,1)
        datapoints = rotM.dot(datapoints)
        datapoints = datapoints[:2,].astype(np.int32).T
        return datapoints

    def putMask(self, srcMask, pos):
        height, x0, y0, angel = pos
        newwidth = int(srcMask.shape[1]*height*1.0/srcMask.shape[0])
        srcMask = cv2.resize(srcMask, (newwidth, height))
        srcMask = rotate_bound(srcMask, angel)
        x0 = x0 + srcMask.shape[1]/2
        y0 = y0 + srcMask.shape[0]/2
        adapted_mask = np.zeros((self.height + 2*srcMask.shape[0], self.width + 2*srcMask.shape[1]), 'uint8')
        if x0 > self.width or x0 < srcMask.shape[1]:
            self.overlap = True
        else:
            self.overlap = False
        adapted_mask[y0:(y0 + srcMask.shape[0]), x0:(x0+srcMask.shape[1])] = srcMask        
        adapted_mask = adapted_mask[srcMask.shape[0]:-srcMask.shape[0], srcMask.shape[1]:-srcMask.shape[1]]
        return adapted_mask

    def createNameGen(self):
        if self.fullnames is None:
            self.data = pd.read_csv('/home/loitg/workspace/genreceipt/resource/temp.csv', encoding='utf-8')
            self.fullnames = self.data['ho va ten'].values
        def f():
            temp = np.random.choice(self.fullnames, 2)
            hogen = temp[0].strip().split(' ')[:random.randint(1,2)]
            hogen = ' '.join([x.upper() for x in hogen])
            tengen = temp[1].strip().split(' ')[-random.randint(1,2):]
            tengen = ' '.join([x.upper() for x in tengen])
            return hogen + ' ' + tengen
        self.namegen = LambdaGen(f)
        return self.namegen

    def createNguyenQuan(self):
        self.tinhtp = pd.read_csv('/home/loitg/workspace/genreceipt/resource/tinhtp.csv', encoding='utf-8')
        sep = RegExGen('[ ]?,[ ]?')
        def f1():
            row = self.tinhtp.sample(1)
            if np.random.rand() < 0.5:
                a = quan(row['quanhuyen'].iloc[0])
                return a
            else:
                b = tinh(row['tinhtp'].iloc[0])
                return b
        def f2():
            row = self.tinhtp.sample(1)
            a = quan(row['quanhuyen'].iloc[0])
            b = tinh(row['tinhtp'].iloc[0])
            return a + sep.gen() + b
        
        self.nguyenquan1 = LambdaGen(f1)
        self.nguyenquan2 = LambdaGen(f2)
        
        return self.nguyenquan1, self.nguyenquan2
    
    def createThuongTru1(self):
        self.thuongtru = None
    
    def buildGuillocheBG(self):
        alpha= np.zeros((self.height, self.width),'uint8')
        amp = random.randint(self.height/7, self.height/5)
        wavelength = random.randint(self.height/4, self.height/2)
        thick = random.randint(1,2)
        angle= random.uniform(0.0, 160.0)
        n = random.randint(15,30)
        y0 = random.randint(20,30)
        dy = (self.height - y0)/n
        x0 = random.randint(20,30)
        dx = (self.width - x0)/n
        
        for i in range(n):
            x0 += dx + random.randint(-2,2)
            y0 += dy + random.randint(-2,2)
            pts = self.sineWave(x0, y0, int(self.width*0.8), amp, wavelength, angle)
            cv2.polylines(alpha, [pts], isClosed=False, color=255, thickness=thick)
        
        return Layer(alpha=alpha, color=self.guilloche_col)            


    def genKeyValuePair(self):
        
        p_line = np.random.rand()
        p_font = np.random.rand()
        afont = None
        var = 0
        numspot = 0
        if p_font < 0.6: # typewriter -- travelling
            afont = self.createParametricFont('travel')
            var = np.random.randint(0,6)
            numspot = np.random.randint(20,30)
        else: # chu in -- para or parab
            afont = self.createParametricFont('pala.ttf')
        
        if p_line < 0.333: # Name
            keytxt = u' tên:' + u'.'*100
            valuetxt = self.namegen.gen()
#             valuetxt = u'TRƯƠNG GIA LỢI'
            self.width = random.randint(550,648)
        elif p_line < 0.666: # Nguyenquan 1
            keytxt = u'tuán:' + u'.'*100
            valuetxt = self.nguyenquan1.gen()
            self.width = random.randint(459, 548)
        else: # Nguyen quan 2
            keytxt = u'tttt:' + u'.'*100
            valuetxt = self.nguyenquan2.gen()
            self.width = random.randint(720, 764)
        
        if np.random.rand() < 0.02:
            valuetxt = u' '
        self.buildCommonParams()
        key_x0 = int( self.p.new('key_x0', self.width/2, paramrange=(0,self.width)).x )
        key_y0 = int( self.p.new('key_y0', self.height/2, paramrange=(0,self.height)).x)
        x0 = int( self.p.new('value_x0', self.width/2, paramrange=(0,self.width)).x )
        y0 = int( self.p.new('value_y0', self.height/2, paramrange=(0,self.height)).x)        
        keyfont = self.createParametricFont('arial')
        key_a = self.p.new('key_angle', 0, paramrange=(-5,5)).x
        value_a = self.p.new('value_angle', 0, paramrange=(-5,5)).x
        key_height = int( self.p.new('key_height', 0.5, paramrange=(0.3,0.8)).x * self.height )
        value_height = int( self.p.new('value_height', 0.5, paramrange=(0.3,0.8)).x * self.height )
        
        mask, txt = self.renderer.toMask2(keyfont, txt=keytxt)
        adapted_mask = self.putMask(mask, (key_height, key_x0, key_y0, key_a)) 
        lnamekey = Layer(alpha= adapted_mask, color=self.text_col)

        mask, txt = self.renderer.toMask2(afont, txt=valuetxt, var=var)
        adapted_mask = self.putMask(mask, (value_height, x0, y0, value_a))
        if self.overlap:
            return None, None
        lnameval = Layer(alpha= adapted_mask, color=self.text_col)       

        above = rstr.rstr('ABC0123456789abcdef ', len(valuetxt))
        below = rstr.rstr('ABC0123456789abcdef ', len(valuetxt))
        mask, txtabove = self.renderer.toMask2(afont, txt=above)
        print mask.shape
        adapted_mask = self.putMask(mask, (self.height/2, random.randint(0, self.width), -self.height/8, value_a))
        labove = Layer(alpha= adapted_mask, color=self.text_col) 
        labove.alpha = random.uniform(0.4,0.95) * labove.alpha
        mask, txtbelow = self.renderer.toMask2(afont, txt=below)
        adapted_mask = self.putMask(mask, (self.height/2, random.randint(0, self.width), self.height*9/8, value_a))
        lbelow = Layer(alpha= adapted_mask, color=self.text_col)
        lbelow.alpha = random.uniform(0.4,0.95) * lbelow.alpha      
        
        lGuiBG = self.buildGuillocheBG()
        l_bg = Layer(alpha=255*np.ones((self.height, self.width),'uint8'), color=self.bg_col)
        ### EFFECTS
        lGuiBG.alpha = random.uniform(0.4,0.7) * lGuiBG.alpha
        lnamekey.alpha = random.uniform(0.4,0.95) * lnamekey.alpha
        lnameval.alpha = self.si.inkeffect(lnameval.alpha, numspot=numspot)
        lnameval.alpha = self.si.matnet(lnameval.alpha)
        if numspot > 0:
            lnameval.alpha = self.si.sonhoe(lnameval.alpha)
#         lnameval.alpha = self.si.blur(lnameval.alpha)
        ### MERGES
        layers = [lnameval, lnamekey, labove, lbelow, lGuiBG, l_bg]
        blends = ['normal'] * len(layers)
        nameline = self.colorize.merge_down(layers, blends).color
        nameline = self.si.addnoise(nameline)
        nameline = self.si.heterogeneous(nameline)
        nameline = self.si.distort(nameline)
#         nameline = self.si.colorBlob(nameline)
        return nameline, no_accent_vietnamese(txt)     
        
    def createParametricFont(self, fontname):
        try:
            afont = self.keyfonts.genByName(fontname)
        except Exception:
            afont = self.valuefonts.genByName(fontname)
        temp = self.p.new(fontname + '_s2h', 0.1).x
        afont.s2h = (temp,temp)
        temp = self.p.new(fontname + '_w2h', 1.0).x
        afont.w2h = (temp,temp)
        return afont       



   
    def buildNameKey(self, height, angel):
        x0 = int( self.p.new('namekey_x0', self.width/2, paramrange=(0,self.width), freeze=True).x )
        y0 = int( self.p.new('namekey_y0', self.height/2, paramrange=(0,self.height), freeze=True).x)
        txt = 'Họ tên:' + '.'*80      
        afont = self.keyfonts.genByName('arial')
        temp = self.p.new('kelltype_s2h', 1.0).x
        afont.s2h = (temp,temp)
        temp = self.p.new('kelltype_w2h', 1.0).x
        afont.w2h = (temp,temp)
        mask, txt = self.renderer.toMask2(afont, txt=txt)
        adapted_mask = self.putMask(mask, (height, x0, y0, angel))
        return Layer(alpha= adapted_mask, color=self.text_col)
    def buildName(self, txt, height, angel):
        x0 = int( self.p.new('nameval_x0', self.width/2, paramrange=(0,self.width), freeze=True).x )
        y0 = int( self.p.new('nameval_y0', self.height/2, paramrange=(0,self.height), freeze=True).x)
        afont = self.valuefonts.genByName('traveling') #Kingthings,Olivetti, traveling, pala.ttf, palab.ttf
        temp = self.p.new('nametype_s2h', 1.0, freeze=True).x
        afont.s2h = (temp,temp)
        temp = self.p.new('nametype_w2h', 1.0, freeze=True).x
        afont.w2h = (temp,temp)
        mask, txt = self.renderer.toMask2(afont, txt=txt)
        #move mask
        adapted_mask = self.putMask(mask, (height, x0, y0, angel))
        return Layer(alpha= adapted_mask, color=self.text_col)
    
    
    
    
    
    def buildOtherLines(self, angle):
        mask, txt = self.renderer.toMask2(self.keyfonts.genByName('arial'), txt='CHUNG MINH NHAN DAN')
        #move mask
        #TODO randomize 
        adapted_mask = self.putMask(mask, (self.height/2, self.width/2,-self.height/4,angle))
        
        return Layer(alpha= adapted_mask, color=self.sodo_col)
    

    
    def buildDOBKey(self, height, angel):
        x0 = int( self.p.new('dobkey_x0', self.width/2, paramrange=(0,self.width), freeze=True).x )
        y0 = int( self.p.new('dobkey_y0', self.height/2, paramrange=(0,self.height), freeze=True).x)
        txt = 'Sinh ngày:' + '.'*80      
        afont = self.keyfonts.genByName('arial')
        temp = self.p.new('kelltype_s2h', 1.0, freeze=True).x
        afont.s2h = (temp,temp)
        temp = self.p.new('kelltype_w2h', 1.0, freeze=True).x
        afont.w2h = (temp,temp)
        mask, txt = self.renderer.toMask2(afont, txt=txt)
        adapted_mask = self.putMask(mask, (height, x0, y0, angel))
        return Layer(alpha= adapted_mask, color=self.text_col)
    
    def buildDOB(self, txt, height, angel, p_chuin=0.3):
        x0 = int( self.p.new('dobval_x0', self.width/2, paramrange=(0,self.width), freeze=True).x )
        y0 = int( self.p.new('dobval_y0', self.height/2, paramrange=(0,self.height), freeze=True).x)
        p = np.random.rand()
#         if p < (1 - p_chuin)/2:
#             afont = self.valuefonts.genByName('Olivetti') #Kingthings,Olivetti, pala.ttf, palab.ttf
#             temp = self.p.new('dob_olivette_s2h', 1.0, freeze=True).x
#             afont.s2h = (temp,temp)
#             temp = self.p.new('dob_olivette_w2h', 1.0, freeze=True).x
#             afont.w2h = (temp,temp)
        if p < (1 - p_chuin):
            afont = self.valuefonts.genByName('Kingthings') #Kingthings,Olivetti, pala.ttf, palab.ttf
            temp = self.p.new('dob_kingthings_s2h', 1.0, freeze=True).x
            afont.s2h = (temp,temp)
            temp = self.p.new('dob_kingthings_w2h', 1.0, freeze=True).x
            afont.w2h = (temp,temp)           
        else:
            afont = self.valuefonts.genByName('pala.ttf') #Kingthings,Olivetti, pala.ttf, palab.ttf
            temp = self.p.new('dob_pala_s2h', 1.0).x
            afont.s2h = (temp,temp)
            temp = self.p.new('dob_pala_w2h', 1.0).x
            afont.w2h = (temp,temp)             
        mask, txt = self.renderer.toMask2(afont, txt=txt)
        #move mask
        adapted_mask = self.putMask(mask, (height, x0, y0, angel))
        return Layer(alpha= adapted_mask, color=self.text_col)
    
        
    def buildID(self, txt, height, angel, p_den=1.1):
        if np.random.rand() < p_den:
            afont = self.idfonts.genByName('UTM Helve.ttf')
            temp = self.p.new('idblack_s2h', 1.0).x
            afont.s2h = (temp,temp)
            temp = self.p.new('idblack_w2h', 1.0).x
            afont.w2h = (temp,temp)
            col = self.text_col 
        else:
            afont = self.idfonts.genByName('9thyssen')
            temp = self.p.new('s2h', 1.0, freeze=True).x
            afont.s2h = (temp,temp)
            temp = self.p.new('w2h', 1.0, freeze=True).x
            afont.w2h = (temp,temp)
            col = self.sodo_col
        mask, txt = self.renderer.toMask2(afont, txt=txt)
        adapted_mask = self.putMask(mask, (height, self.x0, self.y0, angel))
        return Layer(alpha= adapted_mask, color=col)
    
    def buildGuillocheBGSo(self, height, angel):
        alpha= np.zeros((self.height, self.width),'uint8')
        dy = height*1.0/5
        x0 = self.x0
        y0 = self.y0 - height/2
        amp = self.p.new('gui_amp', dy/2, freeze=True).x
        wavelength = self.p.new('wavelength', dy*4, freeze=True).x
        length = self.p.new('length', self.height*7, paramrange=(self.height*5, self.height*9), freeze=True).x
        phase = random.randint(0, 360)
        thick = random.randint(1, 2)
        for i in range(6):
            pts = self.sineWave(x0, int(i*dy + y0), length, amp, wavelength, phase=phase)
            cv2.polylines(alpha, [pts], isClosed=False, color=255, thickness=thick)
        rotM = cv2.getRotationMatrix2D((x0,y0),angel,1)
        alpha = cv2.warpAffine(alpha,rotM,(alpha.shape[1], alpha.shape[0]))
        
        return Layer(alpha=alpha, color=self.sodo_col)

    def genDOB(self):
        ### PARAMETERS
        self.buildCommonParams()        
        nameheight = int( self.p.new('dobval_height-scale', 0.5, paramrange=(0.3,0.8), freeze=True).x * self.height )
        namekeyheight = int( self.p.new('dobkey_height-scale', 0.5, paramrange=(0.3,0.8), freeze=True).x * self.height )
        nameangle = self.p.new('angle', 0, paramrange=(-5,5)).x
        ### LAYERS
        txt = self.dobgen.gen()
        lnamekey = self.buildDOBKey(namekeyheight, nameangle)
        lnameval = self.buildDOB(txt, nameheight, nameangle)
        lGuiBG = self.buildGuillocheBG()
        l_bg = Layer(alpha=255*np.ones((self.height, self.width),'uint8'), color=self.bg_col)
        ### EFFECTS
        lGuiBG.alpha = random.uniform(0.4,0.95) * lGuiBG.alpha
        lnamekey.alpha = random.uniform(0.4,0.95) * lnamekey.alpha
        lnameval.alpha = self.si.inkeffect(lnameval.alpha)
        lnameval.alpha = self.si.matnet(lnameval.alpha)
        lnameval.alpha = self.si.sonhoe(lnameval.alpha)
        lnameval.alpha = self.si.blur(lnameval.alpha)
        ### MERGES
        layers = [lnameval, lnamekey, lGuiBG, l_bg]
        blends = ['normal'] * len(layers)
        nameline = self.colorize.merge_down(layers, blends).color
        nameline = self.si.addnoise(nameline)
        nameline = self.si.heterogeneous(nameline)
        nameline = self.si.colorBlob(nameline)
        return nameline, txt
    
    def genName(self):
        ### PARAMETERS
        self.buildCommonParams()        
        nameheight = int( self.p.new('nameval_height-scale', 0.5, paramrange=(0.3,0.8), freeze=True).x * self.height )
        namekeyheight = int( self.p.new('namekey_height-scale', 0.5, paramrange=(0.3,0.8), freeze=True).x * self.height )
        nameangle = self.p.new('angle', 0, paramrange=(-5,5), freeze=True).x
        ### LAYERS
        txt = self.namegen.gen()
        lnamekey = self.buildNameKey(namekeyheight, nameangle)
        lnameval = self.buildName(txt, nameheight, nameangle)
        lGuiBG = self.buildGuillocheBG()
        l_bg = Layer(alpha=255*np.ones((self.height, self.width),'uint8'), color=self.bg_col)
        ### EFFECTS
        lGuiBG.alpha = random.uniform(0.4,0.95) * lGuiBG.alpha
        lnamekey.alpha = random.uniform(0.4,0.95) * lnamekey.alpha
        lnameval.alpha = self.si.inkeffect(lnameval.alpha)
        lnameval.alpha = self.si.matnet(lnameval.alpha)
        lnameval.alpha = self.si.sonhoe(lnameval.alpha)
        lnameval.alpha = self.si.blur(lnameval.alpha)
        ### MERGES
        layers = [lnameval, lnamekey, lGuiBG, l_bg]
        blends = ['normal'] * len(layers)
        nameline = self.colorize.merge_down(layers, blends).color
        nameline = self.si.addnoise(nameline)
        nameline = self.si.heterogeneous(nameline)
        nameline = self.si.colorBlob(nameline)
        return nameline, txt

    def genIDDen(self):
        ### PARAMETERS
        self.buildCommonParams()        
        idheight = int( self.p.new('height-scale', 0.5, paramrange=(0.3,0.8), freeze=True).x * self.height )
        idangle = self.p.new('angle', 0, paramrange=(-5,5), freeze=True).x
        raio_id_gui = self.p.new('idblack_raio_id_gui', 1.2, paramrange=(1.0,1.8)).x
        ### LAYERS
        lGuiBgSo = self.buildGuillocheBGSo(idheight, idangle)
        txt = self.idnumbergen.gen()
        lId = self.buildID(txt, int(idheight*raio_id_gui), idangle, 1.1)
        lOtherLine = self.buildOtherLines(idangle)
        lGuiBG = self.buildGuillocheBG()
        l_bg = Layer(alpha=255*np.ones((self.height, self.width),'uint8'), color=self.bg_col)
        ### EFFECTS
        lGuiBG.alpha = random.uniform(0.4,0.95) * lGuiBG.alpha
        lOtherLine.alpha = random.uniform(0.4,0.95) * lOtherLine.alpha
        lId.alpha = self.si.inkeffect(lId.alpha)
        lId.alpha = self.si.matnet(lId.alpha)
        lId.alpha = self.si.sonhoe(lId.alpha)
        lId.alpha = self.si.blur(lId.alpha)
        lGuiBgSo.alpha = self.si.matnet(lGuiBgSo.alpha)
        lGuiBgSo.alpha = self.si.blur(lGuiBgSo.alpha)
        ### MERGES
        layers = [lId, lGuiBgSo, lOtherLine, lGuiBG, l_bg]
        blends = ['normal'] * len(layers)
        idline = self.colorize.merge_down(layers, blends).color
        idline = self.si.addnoise(idline)
        idline = self.si.heterogeneous(idline)
        idline = self.si.colorBlob(idline)
        return idline, txt
                

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

    def genID(self):
        ### PARAMETERS
        self.buildCommonParams()        
        idheight = int( self.p.new('height-scale', 0.5, paramrange=(0.3,0.8), freeze=True).x * self.height )
        idangle = self.p.new('angle', 0, paramrange=(-5,5), freeze=True).x
        raio_id_gui = self.p.new('raio_id_gui', 1.2, paramrange=(1.0,1.8), freeze=True).x
        ### LAYERS
        lGuiBgSo = self.buildGuillocheBGSo(idheight, idangle)
        txt = self.idnumbergen.gen()
        lId = self.buildID(txt, int(idheight*raio_id_gui), idangle, 0.0)
        lOtherLine = self.buildOtherLines(idangle)
        lGuiBG = self.buildGuillocheBG()
        l_bg = Layer(alpha=255*np.ones((self.height, self.width),'uint8'), color=self.bg_col)
        ### EFFECTS
        lGuiBG.alpha = random.uniform(0.4,0.9) * lGuiBG.alpha
        lOtherLine.alpha = random.uniform(0.4,0.9) * lOtherLine.alpha
        lId.alpha = self.si.inkeffect(lId.alpha)
        lId.alpha = self.si.matnet(lId.alpha)
        lId.alpha = self.si.sonhoe(lId.alpha)
        lId.alpha = self.si.blur(lId.alpha)
        lGuiBgSo.alpha = self.si.matnet(lGuiBgSo.alpha)
        lGuiBgSo.alpha = self.si.blur(lGuiBgSo.alpha)
        ### MERGES
        layers = [lId, lGuiBgSo, lOtherLine, lGuiBG, l_bg]
        blends = ['normal'] * len(layers)
        idline = self.colorize.merge_down(layers, blends).color
        idline = self.si.addnoise(idline)
        idline = self.si.heterogeneous(idline)
        idline = self.si.colorBlob(idline)
        return idline, txt
    
if __name__ == '__main__':
    c9gen = Stack(608, 80, Params())
    c9gen.createNameGen()
    c9gen.createNguyenQuan()
    for i in range(200): 
        txt = c9gen.nguyenquan1.gen()
        print '---' + txt + '---'
        txt = c9gen.nguyenquan2.gen()
        print '+++' + txt + '+++'
        continue
        img, txt = c9gen.genKeyValuePair()
        if img is None: continue
        print '---' + txt + '---'
        cv2.imshow('hihi', img)
        cv2.waitKey(-1)
        
        
    