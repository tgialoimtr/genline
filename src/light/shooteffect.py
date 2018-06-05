
import os, sys
# Config PYTHONPATH and template folder relatively according to current file location
project_dir = os.path.dirname(__file__) + '/../'
sys.path.insert(0, project_dir)
# from synthgen import *
import cv2
import numpy as np
from Operations import Distort, RotateRange
from PIL import Image

class ShootEffect(object):
    '''
    Includes: resize, jpeg artifact , blur (horizen, vertical), matnet, distort/warp, curved line, noise(above/below), foldeffect, bg(logo))
    '''
    def __init__(self):
        self.p_artifact = 0.3
        self.p_blur = 0.2
        self.p_distort = 0.3
        self.p_curved = 0.1
        self.otherline_noise = 0.4
        self.noise = 0.1
        self.fold_warp =  0.2
        self.p_matnet = 0
        self.p_ = 0
        self.distortor = Distort(0.99,2,2, 4)
        self.rotator = RotateRange(0.99, 2,2)

    # mask
    def matnet(self, mask):
        nplaces = int(mask.shape[1] / mask.shape[0] * 40 * (np.random.rand() +0.5) )
        holesmask = noiseMask(mask, nplaces=nplaces, relative_r=0.1, strength=(0.3,0.8), bsz=1.0)
        return (mask*(1.0-holesmask)).astype(np.uint8)
    
    # textmask
    def sonhoe(self, idtextmask):
        kernel = np.random.randint(1,5)
        idtextmask = cv2.dilate(idtextmask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel,kernel)))
        nhoe = np.random.uniform(0.5, 1.0)
        return idtextmask * nhoe
        
        
    # color image
    def heterogeneous(self, line):
        nplaces = int(line.shape[1] / line.shape[0] * 5 * (np.random.rand()+0.5))
        holesmask0 = 1.0 - noiseMask(line[:,:,0], nplaces=nplaces, relative_r=0.5, strength=(0.05, 0.15), bsz=line.shape[0]/2)
        holesmask1 = 1.0 - noiseMask(line[:,:,0], nplaces=nplaces, relative_r=0.5, strength=(0.05, 0.15), bsz=line.shape[0]/2)
        holesmask2 = 1.0 - noiseMask(line[:,:,0], nplaces=nplaces, relative_r=0.5, strength=(0.05, 0.15), bsz=line.shape[0]/2)
        holesmask = np.stack([holesmask0, holesmask1, holesmask2], axis=2)
        line = line*holesmask
        return line.astype(np.uint8)
    
    # textmask
    def inkeffect(self, mask):
        nplaces = mask.shape[1] / mask.shape[0] * 4 * np.random.rand() ** 2
        mask = inkeffect(mask, nplaces=int(nplaces), strength=0.1)
        return mask
    
    # textmask
    def blur(self, mask):
        (h,_) = mask.shape[:2]
        ksz = h//4*2+1
        bszx= 2*np.random.rand()
        bszy= 2*np.random.rand()
        if bszx + bszy > 2.0:
            return mask
        else:
            mask = cv2.GaussianBlur(mask,(ksz,ksz),sigmaX=bszx, sigmaY=bszy)
            return mask.astype(np.uint8)
    
    # color image
    def addnoise(self, line):
        noises = np.random.randn(*line.shape[:2])*np.random.randint(1,10)
        noises = noises[:,:,np.newaxis] + np.random.randn(*line.shape)*np.random.randint(1,3)
        line = (line + noises)
        line = np.clip(line, 0, 255).astype(np.uint8)
        return line
    
    # color image
    def colorBlob(self, line):
        colormask = noiseMask(line[:,:,0], nplaces=3, relative_r=0.5, strength=(0.2,0.2), bsz=0.1)
        logo_cl = np.random.randint(150,250, size=3)
        rs = (((1-colormask)*1.0)[:,:,np.newaxis] * line
                    + colormask[:,:,np.newaxis]*logo_cl    ) 
        return np.clip(rs,0,255).astype(np.uint8)
        
    
    def combine(self, textmask, bg_cl, fg_cl):
        textmask = textmask/255.0
        rs = (((1-textmask)*1.0)[:,:,None] * bg_cl
                    + textmask[:,:,None]*fg_cl    )
        return np.clip(rs,0,255).astype(np.uint8)

    # image
    def lowresolution(self, img):
        realheight = np.random.randint(13,32)
        r = realheight*1.0/img.shape[0]
        img = cv2.resize(img, (0,0), fx = r, fy = r)
        img = cv2.resize(img, (0,0), fx = 1.0/r, fy = 1.0/r)
        return img
    
    # image
    def jpegartifact(self, img):
        q = np.random.randint(40,90)
        cv2.imwrite('/tmp/789789789.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, q])
        img = cv2.imread('/tmp/789789789.jpg')
        return img
    
    # image
    def rotate(self, img):
        pilimg = Image.fromarray(img)
        pilimg = self.rotator.perform_operation(pilimg)             
        img = np.array(pilimg)
        return img

    # image
    def distort(self, img):
        pilimg = Image.fromarray(img)   
        pilimg = self.distortor.perform_operation(pilimg)
        img = np.array(pilimg)
        return img

    # image
    def addMep(self, img):
        bg_cl = np.random.randint(40,140) + np.random.randn(3)*np.random.randint(2,10)
        bg_cl = np.clip(bg_cl, 0, 255).astype(int)
        pad = np.random.randint(img.shape[0]/4+1, img.shape[0]+1)
        newimg = np.zeros((img.shape[0],img.shape[1]+pad,3), np.uint8)
        if np.random.rand() < 0.5:
            newimg[:,:pad] = bg_cl
            newimg[:,pad:] = img
        else:
            newimg[:,-pad:] = bg_cl
            newimg[:,:-pad] = img
        return newimg
    
    
    def effect(self, textmask):
        # Select colors
        bg_main_cl = np.random.randint(190,250) + np.random.randn(3)*np.random.randint(1,5)
        bg_main_cl = np.clip(bg_main_cl, 0, 255).astype(int)
        fg_main_cl = np.random.randint(40,140) + np.random.randn(3)*np.random.randint(2,10)
        fg_main_cl = np.clip(fg_main_cl, 0, 255).astype(int)
        # Textmask
        if np.random.rand() < 0.6:
            textmask = self.matnet(textmask)
#         cv2.imshow('matnet', textmask)
        if np.random.rand() < 0.5:
            textmask = self.blur(textmask)
#         cv2.imshow('blur', textmask)
#         print 'textmask', np.amin(textmask), np.amax(textmask)
        # Combine
        rs = self.combine(textmask, bg_main_cl, fg_main_cl)
#         cv2.imshow('combine', rs)
#         print 'combine', np.amin(rs), np.amax(rs)
        # Image
        if np.random.rand() < 0.1:
            rs = self.colorBlob(rs)
#         cv2.imshow('colorblob', rs)
#         print 'colorblob', np.amin(rs), np.amax(rs)
        if np.random.rand() < 0.3:
            rs = self.heterogeneous(rs)
#         cv2.imshow('hete', rs)
#         print 'hete', np.amin(rs), np.amax(rs)
        if np.random.rand() < 0.4:
            rs = self.distort(rs)
#         cv2.imshow('distort', rs)
#         print 'distotrt', np.amin(rs), np.amax(rs)
#         cv2.imwrite('/tmp/uiui123.tiff', rs)
#         if np.random.rand() < 0.99:
#             rs = self.rotate(rs)
#         cv2.imshow('rotate', rs)
#         print 'rotate', np.amin(rs), np.amax(rs)
        if np.random.rand() < 0.15:
            rs = self.addMep(rs)
        if np.random.rand() < 0.99:
            rs = self.addnoise(rs)
#         cv2.imshow('noise', rs)
#         print 'noise', np.amin(rs), np.amax(rs)
        if np.random.rand() < 0.99:
            rs = self.jpegartifact(rs)
#         cv2.imshow('artifact', rs)
#         print 'artifact', np.amin(rs), np.amax(rs)
        if np.random.rand() < 0.99:
            rs = self.lowresolution(rs)
#         cv2.imshow('lowreslution', rs)
#         print 'shooteffect', np.amin(rs), np.amax(rs)
        return rs

def noiseMask(oritext, nplaces=20, relative_r=0.1, strength=(0.0,1.0), bsz=4):   
    rmask = np.zeros_like(oritext, dtype=np.float)
    (h,w) = oritext.shape[:2]
    ksz = h//4*2+1
    for i in range(nplaces):
        r = int(relative_r*h)
        if r < 1: continue
        r = np.random.randint(r)
        inten = np.random.uniform(strength[0], strength[1])
        y = np.random.randint(h)
        x = np.random.randint(w)
        cv2.circle(rmask,(x,y), r, inten, -1)
    rmask = cv2.GaussianBlur(rmask,(ksz,ksz), sigmaX=bsz, sigmaY=bsz)
#     cv2.imshow('h', rmask*1.0/np.amax(rmask))
#     cv2.waitKey(-1) 
    return rmask 
       
    
def inkeffect(oritext, nplaces=20, strength=0.1, onlyshrink=False):
    rs = np.zeros_like(oritext)
    (h,w) = oritext.shape[:2]
    rmask = noiseMask(oritext, nplaces, relative_r=0.1, strength=(-0.1*h, +0.1*h))
    
    for x in range(0,w):
        for y in range(0,h):
            r = int(rmask[y,x])
            if r == 0:
                rs[y,x] = oritext[y,x]
            elif r > 0:
                xmin = max(0, x - r)
                xmax = min(w-1, x + r)
                ymin = max(0, y - r)
                ymax = min(h-1, y + r)
                rs[y,x] = np.amax(oritext[ymin:ymax, xmin:xmax])
            elif r < 0:
                xmin = max(0, x + r)
                xmax = min(w-1, x - r)
                ymin = max(0, y + r)
                ymax = min(h-1, y - r)
                rs[y,x] = np.amin(oritext[ymin:ymax, xmin:xmax])

#     cv2.imshow('h', rs)
#     cv2.waitKey(-1)            
    
    return rs  


def init():
    si = ShootEffect()
    # Select colors
    bg_main_cl = np.random.randint(190,250) + np.random.randn(3)*np.random.randint(1,5)
    bg_main_cl = np.clip(bg_main_cl, 0, 255).astype(int)
    fg_main_cl = np.random.randint(2,150) + np.random.randn(3)*np.random.randint(2,10)
    fg_main_cl = np.clip(fg_main_cl, 0, 255).astype(int)
    # Create texts
    
    textmask = np.zeros((32, 270), dtype=np.uint8)
    font = cv2.FONT_HERSHEY_PLAIN
    cv2.putText(textmask,'Bedoc Mall 123         $  19.09',(5,20), font, 1.0,255,2,cv2.LINE_AA)
    # Textmask
    if np.random.rand() < 0.99:
        textmask = si.matnet(textmask)
    if np.random.rand() < 0.99:
        textmask = si.blur(textmask)    
    # Combine
    rs = si.combine(textmask, bg_main_cl, fg_main_cl)
    # Image
#     if np.random.rand() < 0.3:
#         rs = si.colorBlob(rs)
#     if np.random.rand() < 0.3:
#         rs = si.heterogeneous(rs)
    if np.random.rand() < 0.99:
        rs = si.distort(rs)
#     if np.random.rand() < 0.3:
#         rs = si.rotate(rs)
    if np.random.rand() < 0.99:
        rs = si.addnoise(rs)
#     if np.random.rand() < 0.3:
#         rs = si.jpegartifact(rs)
#     if np.random.rand() < 0.3:
#         rs = si.lowresolution(rs)


    cv2.imshow('ll',rs)
    cv2.waitKey(-1)
    
    print '------------'
    
    return None     
############################################################################    
if __name__ == '__main__':
    for i in range(30):
        line = init()
    
def feather(text_mask, min_h):
    # determine the gaussian-blur std:
    if min_h <= 15 :
        bsz = 0.25
        ksz=1
    elif 15 < min_h < 30:
        bsz = max(0.30, 0.5 + 0.1*np.random.randn())
        ksz = 3
    else:
        bsz = max(0.5, 1.5 + 0.5*np.random.randn())
        ksz = 5
    return cv2.GaussianBlur(text_mask,(ksz,ksz),bsz)
    