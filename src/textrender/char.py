'''
Created on Jun 5, 2018

@author: loitg
'''
import pygame.locals
from pygame import freetype
import cv2
    
class PrintedChar(object):
    '''
    classdocs
    '''
    
    def __init__(self, ch):
        if ch == ' ':
            raise ValueError()
        self.ch = ch
        self.spaceWidthAdj = 0.0
        self.basefont = None
        self.baseheight = None
    
    def setFont(self, basefont, height, ratios=(1.0,1.0)):
        reinit = False
        if self.basefont is None:
            if basefont is None:
                raise ValueError('construct null')
            else:
                reinit = True
                self.basefont = basefont
        else:
            if basefont is not None and self.basefont != basefont:
                reinit = True
                self.basefont = basefont
        if self.baseheight is None:
            if height is None:
                raise ValueError('construct null')
            else:
                reinit = True
                self.baseheight = height                
        else:
            if height is not None and self.baseheight != height:
                reinit = True
                self.baseheight = height
        if reinit:
            self.font = freetype.Font(self.basefont, size=self.baseheight)
            self.font.antialiased = True
            self.font.origin = True
            self.space = self.font.get_rect('O')
        if ratios is not None:
            self.r_x = ratios[0]
            self.r_y = ratios[1]
        
    def spaceWidth(self):
        return self.space.width
    
    def normHeight(self):
        return self.baseheight
        
    def render(self, (x,y), shape):
        x = int(x)
        y = int(y)
        pgsurf = pygame.Surface((shape[1], shape[0]), pygame.locals.SRCALPHA, 32)
        bound = self.font.render_to(pgsurf, (x,y), self.ch)
        bound.x = x + bound.x
        bound.y = y - bound.y
        mask = pygame.surfarray.pixels_alpha(pgsurf)
        mask = mask.swapaxes(0,1)
#         if self.r_x != 1.0 or self.r_y != 1.0:
#             mask2 = cv2.resize(mask, None, fx=self.r_x, fy=self.r_y)
#             bound.width = bound.width * self.r_x
#             bound.height = bound.height * self.r_y
#             dx = bound.x * (self.r_x - 1.0)
#             mask2 = mask2[:,:]
        return bound, mask

    