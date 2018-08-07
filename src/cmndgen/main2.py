# -*- coding: utf8 -*-
'''
Created on Aug 6, 2018

@author: loitg
'''
import cv2, os
import json
import codecs
import numpy as np
from cmndgen.pipeline import CMNDPipeID, CMNDPipeName
from textgen.vnnames import HoTenGen, QuanHuyenGen
from utils.common import RESOURCE_PATH, TEMPORARY_PATH

def to_weinman(root):
    pipe_name = CMNDPipeName()
    hotengen = HoTenGen(os.path.join(RESOURCE_PATH, 'hovaten.csv'))
    quanhuyengen = QuanHuyenGen(os.path.join(RESOURCE_PATH, 'tinhtp.csv'))
    filecontent = codecs.open(TEMPORARY_PATH + '4/aligned.txt', encoding='utf8').read()
    jsonStr = filecontent.replace('\'', '"')
    jsonObj = json.loads(jsonStr)
    with codecs.open(root + 'anno-train.txt', 'a', encoding='utf8') as annotation_train:
        with codecs.open(root + 'anno-test.txt', 'a', encoding='utf8') as annotation_test:
            for i in range(1, 3000):
                print i, '-----------------------'
                p = np.random.rand()
                if p < 0.5:
                    pipe_name.txt =hotengen.gen()
                else:
                    pipe_name.txt = quanhuyengen.gen()
                
                pipe_name.p.reset(jsonObj)
                rs, _, txt = pipe_name.gen()
                if rs is None: continue
                txt = txt.strip()
#                 newwidth = rs.shape[1] * 32.0 / rs.shape[0]
#                 rs = cv2.resize(rs, (int(newwidth), 32))
                cv2.imwrite(root + str(i) + '.jpg', rs)
#                 print '@@@'+txt+'@@@'
#                 cv2.imshow('hihi', rs)
#                 cv2.waitKey(-1)
#                 continue
                if i < 2900:
                    annotation_train.write('./' + str(i) + '.jpg ' + txt + '\n')
                else:
                    annotation_test.write('./' + str(i) + '.jpg ' + txt + '\n')

def to_rcnn():
    pass

if __name__ == '__main__':
    to_weinman('/home/loitg/Downloads/images_cmnd_chu/')
    