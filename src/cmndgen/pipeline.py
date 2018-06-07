'''
Created on Jun 5, 2018

@author: loitg
'''
import numpy as np
from paramatch.collections import Params
from font.font import Printed
from textrender.textrenderer import RelPosRenderer

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