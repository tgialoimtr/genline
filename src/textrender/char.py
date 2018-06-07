'''
Created on Jun 5, 2018

@author: loitg
'''
import pygame
from pygame import freetype
import numpy as np

class PrintedChar(object):
    '''
    classdocs
    '''
    
    def __init__(self, ch):
        if ch == ' ':
            raise ValueError()
        self.ch = ch
        self.spaceWidthAdj = 0.0
    
    def setFont(self, basefont, height):
        self.basefont = basefont
        self.baseheight = height
        self.font = freetype.Font(self.basefont, size=self.height)
        self.space = self.font.get_rect('O')
        
    def spaceWidth(self):
        return self.space.width
    
    def normHeight(self):
        return self.baseheight
        
    def putAt(self, (x,y), surface):
        surface = np.zeros_like(surface)
        x = int(x)
        y = int(y)
        surf = pygame.Surface(surface.shape, pygame.locals.SRCALPHA, 32)
        bounds = self.font.render_to((x,y), surf, self.ch)
        
        bounds.x = x + bounds.x
        bounds.y = y - bounds.y
                
        surf = pygame.surfarray.pixels_alpha(surf)

        return bounds, surf

class HandWrittenChar(object):
    
    @staticmethod
    def createFromDB(database_dir):
        font = {}
        dau = {}
        thanh = {}
        
        font['a'] = HandWrittenChar()
        
        return font
    
    def __init__(self):
        # read database
        self.samples = []

    def __distort(self):
        #pick random sample, then distort
        pass
    
    def putAt(self, surface):
        #distort
        
        #stroke width
        self.strokeWidth
        
        
        return surface   
        
    
    