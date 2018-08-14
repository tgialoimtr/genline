'''
Created on Jun 16, 2018

@author: loitg
'''
import cv2
import numpy as np
import pandas as pd
import os, sys
from glob import glob
import pygame
from mnist import MNIST
from textrender.char import PrintedChar
from utils.common import summarize
from utils.common import RESOURCE_PATH

class TTFFont(object):

    def __init__(self, charset, height, basefont, ratios=(1.0,1.0)):
        pygame.init()
        self.charfont = {}
        self.charset = charset
        for c in charset:
            self.charfont[c] = PrintedChar(c)
            self.charfont[c].setFont(basefont, height, ratios)
        
    
    def overWrite(self, ch, newheight=None, newbasefont=None, ratios=(1.0,1.0)):
        if ch != ' ':
            self.charfont[ch].setFont(newbasefont, newheight, ratios)
    
    def render(self, ch, pos, shape=None):
        (x,y) = pos
        return self.charfont[ch].render((x,y), shape)
    
    def spaceWidth(self):
        return list(self.charfont.values())[0].spaceWidth()
    def normHeight(self):
        return list(self.charfont.values())[0].normHeight()
        
class ClassAutoBalancedLoader(object):
    ''' 
    Future Implement Queue
    '''
    def __init__(self):
        pass
    def loadNextBatch(self, maxinstances = None):
        pass


class SomeOnRamLoader(object):
    '''
    Load all data to RAM, and return part of them
    '''
    def __init__(self, database_dir, databse_type):
        self.currentBatch = None
        self.database_dir = database_dir
        self.databse_type = databse_type
    
    def loadNextBatch(self, maxinstances = 100):
        '''
        writer(string): id of writer
        disposable(bool): Client no long use this sample, should dispose for space for next new samples
        '''
        instances = []
        if maxinstances is not None and maxinstances > 0:
            self.maxinstances = maxinstances
        else:
            self.maxinstances = sys.maxint
        if self.databse_type == "EMNIST_original_byclass":
            for folder in glob(self.database_dir + '/*'):
                label = os.path.basename(folder.rstrip(os.path.sep))
                sample_count = 0
                label = int(label, 16)
                if label >= 48 and label <=57: #[0-9]
                    label -= 48
                if label >= 65 and label <= 90: #[A-Z]
                    label -= 55
                if label >= 97 and label <= 122: #[a-z]
                    label -= 61
                for hsf in glob(folder + '/*'):
                    if os.path.isdir(hsf):
                        for img_path in glob(hsf + '/*.png'):
                            img = cv2.imread(img_path) # 128 * 128; 0-255; uint8
#                             cv2.imshow('dd',img)
#                             print summarize(img)
#                             print label
#                             cv2.waitKey(-1)
                            instance = [img, label, '', False]
                            instances.append(instance)
                            sample_count += 1
                            if sample_count == self.maxinstances: break
                            
                        if sample_count == self.maxinstances: break
                        
        elif self.databse_type == "EMNIST_28x28":
            mndata = MNIST(self.database_dir, return_type='numpy')
            mndata.select_emnist('byclass')
            images, labels = mndata.load_testing()
            
            for img, label in zip(images, labels):
                img = np.reshape(img, (28,28)).astype(np.uint8)
#                 print summarize(img) # 28 * 28; 0-255; uint8
#                 print label  
                instance = [img, label, '', False]
                instances.append(instance)
            
        elif self.databse_type == "Char74k":
            sample_count = {}
            for folder in glob(self.database_dir + '/*'):
                if os.path.isdir(folder):
                    for img_path in glob(folder + '/*.png'):
                        img = cv2.imread(img_path) # 900 * 1200; 0-255; uint8
                        label = int(folder[-3:]) - 1
                        instance = [img, label, '', False]
                        instances.append(instance)
                        if label in sample_count:
                            sample_count[label] += 1
                        else:
                            sample_count[label] = 0
                        if sample_count[label] == self.maxinstances: break
        else:
            raise ValueError('db not supported yet')
        
        self.currentBatch = pd.DataFrame(instances, columns=['img', 'label', 'writer', 'disposable'])

 
class HandWrittenFont(object):

    def __init__(self, dataloader, baseheight):
        self.baseheight = baseheight
        self.samples = []
        self.loader = dataloader
        self.loader.loadNextBatch(maxinstances=2)

    def __distort(self):
        #pick random sample, then distort
        pass    
    
    def selectWriter(self, writerid=None):
        pass
    
    def overWrite(self, ch=None, newheight=None):
        if ch == None: ovrChars = self.charset
        for c in self.fontchar:
            pass
                  
    def render(self, ch, pos, shape=None, ratio=None):
        #distort
        
        #stroke width
        self.strokeWidth
        
        self.database.next
        
        return None   
    
    

if __name__ == '__main__':
    charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
    pf = TTFFont(charset, 40, RESOURCE_PATH + 'fontss/receipts/general_fairprice/LEFFC2.TTF')
    pf.overWrite('j', None, None, (1.0,1.5))

#     hwf = HandWrittenFont(SomeOnRamLoader('/media/loitg/New Volume/ocr/bywriteclass/by_class/', "EMNIST_original_byclass"),40)
#     hwf = HandWrittenFont('/media/loitg/New Volume/ocr/English/Hnd/Img', "Char74k", 40)
    
    bound, mask = pf.render('j', (40,40),(100,100))
#     bound, mask = hwf.render('a', (40,40), (100,100))
    
    cv2.imshow('rd', mask)
    print(bound)
    
    
    pf.overWrite('j', None, None, (1.0,1.0))
    bound, mask = pf.render('j', (40,40),(100,100))
    cv2.imshow('rd2', mask)
    print(bound)
    cv2.waitKey(-1)
