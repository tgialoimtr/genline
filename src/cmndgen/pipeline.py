'''
Created on Jun 5, 2018

@author: loitg
'''
import numpy as np
from paramatch.collections import Params
from textrender.textrenderer import RelPosRenderer
from textrender.font import TTFFont
from textrender.relpos_matrix import RelPos4D

class CMNDPipeline(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        self.txt = None
        self.font = Printed()
        self.renderer = None
        
    def initParams(self, gt_text):
        self.txt = gt_text
        self.params = Params()
        self.renderer = RelPosRenderer()
        
        self.renderer.a = self.params.new()
        
        
        
        
    def gen(self):
        
        line = np.array((32,100))
        return line
    
    
    
if __name__ == '__main__':
    charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
     
    ### FONTS
    basefont = '/home/loitg/Downloads/fonts/fontss/receipts/general_fairprice/LEFFC2.TTF'
    ### RelPos
    mat = RelPos4D(charset)
    mat.mat[('a','b')].hor = -0.1
    mat.mat[('1','2')].hor = +0.5
    
    pf = TTFFont(charset, 40, basefont)
    rd = RelPosRenderer(charset, pf)
    
    txt = 'abc123mn'
    mask, charmasks, charbbs, ybaseline = rd.renderFit(txt, 40, mat)
    cv2.imshow('mask', mask)
    for img, bb in zip(charmasks,charbbs):
        cv2.imshow('mask0', img)
        aaa = mask[bb[1]:(bb[1]+bb[3]), bb[0]:(bb[0]+bb[2])]
        cv2.imshow('bb0', aaa)
        cv2.waitKey(-1)
    sys.exit(0)