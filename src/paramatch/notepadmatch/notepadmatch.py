'''
Created on Jul 17, 2018

@author: loitg
'''
import sys, os
import hashlib
import cv2
import numpy as np
from cmndgen.pipeline import CMNDPipeID, CMNDPipeName
from utils.common import gray2heatmap
import json
import codecs
from src.utils.common import TEMPORARY_PATH

class Instance(object):
    def __init__(self, imgpath, gennerFromFile, dst_height=None):
        self.imgpath = imgpath
        self.imgname = os.path.basename(imgpath)
        self.img = cv2.imread(self.imgpath)
        if dst_height is not None:
            newwidth = int(1.0*self.img.shape[1]/self.img.shape[0]*dst_height)
            self.img = cv2.resize(self.img, (newwidth, dst_height))
        self.gen = gennerFromFile
        self.previousmd5 = None
        self.combinedPreview = None
        self.combineColor = 2
        
    def initTextAt(self, workdir):
        self.txtname = self.imgname + '.txt'
        self.txtpath = os.path.join(workdir, self.txtname)
        if not os.path.exists(self.txtpath):
            with open(self.txtpath, 'w'): pass   
        return self.txtpath, self.txtname
    
    def _redraw(self, filecontent):
        line, masks, _ = self.gen(filecontent)
        target_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        if line is None:
            line = np.zeros_like(target_gray, dtype=np.uint8)
            masks = [np.zeros_like(target_gray, dtype=np.uint8)]
        target_heatmap = gray2heatmap(target_gray)*255
        target_heatmap = target_heatmap.astype(np.uint8)
        line_heatmap = gray2heatmap(line)*255
        line_heatmap = line_heatmap.astype(np.uint8)
        
        overlay = masks[0]
        for i in range(1, len(masks)):
            overlay = cv2.bitwise_or(overlay, masks[i])
        
        output = np.zeros_like(self.img, dtype=np.uint8)
        minheight = min(self.img.shape[0], overlay.shape[0])
        minwidth = min(self.img.shape[1], overlay.shape[1])
        output[:minheight,:minwidth,self.combineColor] = overlay[:minheight,:minwidth]
        cv2.addWeighted(output, 0.5, self.img, 0.5, 0, output)
        print output.shape
        print overlay.shape
        self.combinedPreview = stackAndShow([target_heatmap, line_heatmap, output], direction_is_horizontal=True, sameheight=64)
        
        return self.combinedPreview
        
    
    def changed(self, reset=True):
        filecontent = codecs.open(self.txtpath, encoding='utf8').read()
        newmd5 = hashlib.md5(filecontent.encode("utf-8")).hexdigest()
        if newmd5 != self.previousmd5:
            if reset:
                self.previousmd5 = newmd5
            self._redraw(filecontent)
            return True
        else:
            return False
    
    def getPreview(self):
        filecontent = open(self.txtpath).read()
        newmd5 = hashlib.md5(filecontent).hexdigest()
        if newmd5 != self.previousmd5:
            self._redraw(filecontent)
        return self.combinedPreview
    

def stackAndShow(imgs, direction_is_horizontal=True, samewidth=None, sameheight=None):
    if samewidth is None and sameheight is None:
        if direction_is_horizontal:
            sameheight = max([img.shape[0] for img in imgs])
        else:
            samewidth = max([img.shape[1] for img in imgs])
    if sameheight is not None: # all same height
        resizedimgs = [cv2.resize(img, (int(1.0*img.shape[1]/img.shape[0]*sameheight), sameheight)) for img in imgs]
    elif samewidth is not None:
        resizedimgs = [cv2.resize(img, (samewidth, int(1.0*img.shape[0]/img.shape[1]*samewidth))) for img in imgs]
    resizedimgs = [(img if len(img.shape) == 3 and img.shape[2] == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)) for img in resizedimgs]
    maxheight = max([img.shape[0] for img in resizedimgs])
    maxwidth = max([img.shape[1] for img in resizedimgs])
    if direction_is_horizontal:
        rs = np.zeros(shape=(maxheight, maxwidth*len(resizedimgs),3), dtype=np.uint8)
        for i, img in enumerate(resizedimgs):
            rs[:img.shape[0], i*maxwidth : img.shape[1] + i*maxwidth] = img
    else:
        rs = np.zeros(shape=(maxheight*len(resizedimgs), maxwidth,3), dtype=np.uint8)
        for i, img in enumerate(resizedimgs):
            rs[i*maxheight : img.shape[0] + i*maxheight, :img.shape[1]] = img
    return rs
        
def measureCompare(linedir, workdir):
    pass

def sample(alignedpath, tempdir):
    pass

if __name__ == '__main__':
    sys.argv = [TEMPORARY_PATH + '35', TEMPORARY_PATH + '4']
    if len(sys.argv) < 2:
        print('linedir, workingdir')
        sys.exit(0)
    
    linedir = sys.argv[0]
    workdir = sys.argv[1]
    pipe = CMNDPipeName()
    def gen(filecontent):
        try:
            txt, jsonStr = filecontent.split('\n', 1)
            jsonStr = jsonStr.replace('\'', '"')
            pipe.txt = txt
            jsonObj = json.loads(jsonStr)
            pipe.p.reset(jsonObj)
            return pipe.gen()
        except Exception as e:
            print('Cannot read file: ' + str(e))
            return None, None, None
        
    
    instances = []
    for fn in os.listdir(linedir):
        if fn[-3:].upper() not in ['PEG','JPG','PNG']:
            continue
        instance = Instance(os.path.join(linedir, fn), gen, dst_height=64)
        instance.initTextAt(workdir)
        instances.append(instance)   
    
    cv2.namedWindow('window')
    previews = [None] * len(instances)
    while True:
        for i, instance in enumerate(instances):
            if instance.changed(reset=True):
                print(instance.imgname + ' redrawing ...')
                preview = instance.getPreview()
                previews[i] = preview
        preview_all = stackAndShow(previews, direction_is_horizontal=False, sameheight=64)
        cv2.imshow('window', preview_all)
        cv2.waitKey(500)
 