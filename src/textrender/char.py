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
        
    def render(self, pos, shape):
        x = int(pos[0])
        y = int(pos[1])
        pgsurf = pygame.Surface((shape[1], shape[0]), pygame.locals.SRCALPHA, 32)
        bound = self.font.render_to(pgsurf, (x,y), self.ch)
        mask = pygame.surfarray.pixels_alpha(pgsurf)
        mask = mask.swapaxes(0,1)
        if self.r_x != 1.0 or self.r_y != 1.0:
            mask9 = cv2.resize(mask, None, fx=self.r_x, fy=self.r_y)
            x9 = int(round(x*self.r_x))
            y9 = int(round(y*self.r_y))
            x0 = 0 - x; x1 = mask.shape[1] - x; y0 = 0 - y; y1 = mask.shape[0] - y;
            x90 = 0 - x9; x91 = mask9.shape[1] - x9; y90 = 0 - y9; y91 = mask9.shape[0] - y9;
            newx0 = max(x0, x90); newx1 = min(x1,x91);
            newy0 = max(y0, y90); newy1 = min(y1,y91);
            x0 = newx0 + x; x1 = newx1 + x; y0 = newy0 + y; y1 = newy1 + y;
            x90 = newx0 + x9; x91 = newx1 + x9; y90 = newy0 + y9; y91 = newy1 + y9;
            mask[:,:] = 0
            mask[y0:y1,x0:x1] = mask9[y90:y91,x90:x91]
            
            bound.width = int(round(bound.width * self.r_x))
            bound.height = int(round(bound.height * self.r_y))
            bound.x = int(round(bound.x * self.r_x))
            bound.y = int(round(bound.y * self.r_y))
        bound.x = x + bound.x
        bound.y = y - bound.y
        return bound, mask


if __name__ == '__main__':
    import pygame
    pygame.init()
    charfont = PrintedChar('a')
    charfont.setFont('/home/loitg/Downloads/fonts/fontss/receipts/general_fairprice/LEFFC2.TTF', 40)
    _, mask = charfont.render((50,50),(100,100))
    cv2.imshow('kk', mask)
    cv2.waitKey(-1)



    