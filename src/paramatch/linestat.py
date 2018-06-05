'''
Created on Feb 11, 2018

@author: loitg
'''
import os
from ocrolib import psegutils,morph,sl
import numpy as np
import cv2
from utils.common import sauvola


class CharAppearance(object):
    def __init__(self, basefont, size):
        self.vscale = 0
        
    def 
    
    
class CustomizedFont(object):
    def __init__(self):
        self.vscale = 0
        
    def charMask(self, ch, font):
        pass
    def locToOrigin(self, ch, width, height, x, y):
        return 0,0
    def render(self, txt, height, char_font_map, kerning_info):
        for ch in txt:
            

class FontStat(object):
    def __init__(self, storename, fontpathlist):
        self.storename = storename
        self.basefonts = []
        for fp in fontpathlist:
            self.basefonts.append(fp)
        self.char_font_map = {}
        
    def analyse(self, line, char_cand, labels):
        prech = None
        for ch in labels:
            candidates = []
            ##for font in basefonts
            ##for size in range()
                # char_mask =  charMask(font, size)
                # match template of mask
                # actual_location = locToOrigin(...)
                # candidates.append((prob, font, size, actual_lcoation))
                
            ### 
                
            
            
            #add top 2 candidates to font map
            pass
        
        
    def finalize(self):
        for ch, font_list in self.char_font_map.iteritems():
            for prob, font, size, actual_lcoation in font_list:
                pass
            self.char_font_map[ch] = CharAppearance(font, size)
        

    
def calc_typo_metric(binline):
    labels,n = morph.label(binline)
    objects = morph.find_objects(labels)
    filtered = []
    max_h = 0
    for o in objects:
        h = sl.dim0(o)
        w = sl.dim1(o)
        if h > binline.shape[0]*0.98: continue
        if h < 3 or w < 3: continue
        if (h > binline.shape[0]*0.2 and w > binline.shape[0]*0.2) or \
                (o[0].start > binline.shape[0]/2 and o[1].stop > binline.shape[1]/4 and o[1].stop < 3*binline.shape[1]/4 and o[0].stop < binline.shape[0]*0.98):
            filtered.append(o)
            if h > max_h:
                max_h = h
    filtered.sort(key=lambda x:x[1].start)
    prech = None
    zoomforsee = 4
    infoheight=50
    info = np.zeros((infoheight*2+binline.shape[0]*zoomforsee,binline.shape[1]*zoomforsee))
    for ch in filtered:
        h = sl.dim0(ch)
        w = sl.dim1(ch)
        if prech is not None and ch[1].start < (prech[1].start + prech[1].stop)/2: continue
        cv2.putText(info,'{:3.2f}'.format(1.0*w/max_h),\
                    ((ch[1].start)*zoomforsee, int(infoheight*0.4)), cv2.FONT_HERSHEY_SIMPLEX, \
                    0.5,1.0,1)
        if prech is None:
            cv2.putText(info,'{:3d}'.format(max_h),\
                        ((ch[1].start)*zoomforsee, int(infoheight*0.9)), cv2.FONT_HERSHEY_SIMPLEX, \
                        0.5,1.0,1)           
        else:    
            space = ch[1].start - prech[1].stop
            dist = ch[1].stop - prech[1].stop
            cv2.putText(info,'{:3.2f}'.format(1.0*space/max_h),\
                        ((prech[1].stop)*zoomforsee, int(infoheight*0.9)), cv2.FONT_HERSHEY_SIMPLEX, \
                        0.5,1.0,1)
            cv2.putText(info,'({:3.2f})'.format(1.0*dist/max_h),\
                        ((prech[1].stop)*zoomforsee, int(infoheight*1.4)), cv2.FONT_HERSHEY_SIMPLEX, \
                        0.5,1.0,1)
        prech = ch
    info[infoheight*2:,:] = cv2.resize(binline, (zoomforsee*binline.shape[1], zoomforsee*binline.shape[0]))
    return (info*250).astype(np.uint8), filtered


if __name__ == '__main__':
    lines_path = '/tmp/realsamples/'
    fontstat = FontStat('test')
    for filename in os.listdir(lines_path):
        mainimgname = filename[:-4]
        line = cv2.imread(lines_path+filename,0)
        binline = sauvola(line,w=line.shape[0]/2, k=0.05, reverse=True)
        info, ch_cand = calc_typo_metric(binline)
        cv2.imshow('jj', info)
        while True:
            k = cv2.waitKey(-1)
            if ord(k) == 'y':
                labels = raw_input('Enter labels: ')
                fontstat.analyse(binline, ch_cand, labels)
                
                break
            elif ord(k) == 'n':
                break
        
        
            