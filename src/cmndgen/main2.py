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
from textgen.vnnames import HoTenGen, QuanHuyenGen, Trash
from utils.common import RESOURCE_PATH, TEMPORARY_PATH
from utils.common import gray2heatmap, resizeToHeight
from textgen.combiner import ListGenWithProb
from textrender.font2 import UnicodeUtil
import re

def to_weinman(root):
    pipe_name = CMNDPipeName()
    hotengen = HoTenGen(os.path.join(RESOURCE_PATH, 'hovaten.csv'))
    quanhuyengen = QuanHuyenGen(os.path.join(RESOURCE_PATH, 'tinhtp.csv'), number=2)
    trashgen = Trash(os.path.join(RESOURCE_PATH, 'hovaten.csv'),0.5)
    filecontent = codecs.open(TEMPORARY_PATH + '4/aligned.txt', encoding='utf8').read()
    jsonStr = filecontent.replace('\'', '"')
    jsonObj = json.loads(jsonStr)
    namegen = ListGenWithProb([hotengen, quanhuyengen, trashgen], [0.4,0.3,0.3])
    unicodeutil = UnicodeUtil(RESOURCE_PATH + 'diacritics2.csv')
    with codecs.open(root + 'anno-train.txt', 'a', encoding='utf8') as annotation_train:
        with codecs.open(root + 'anno-test.txt', 'a', encoding='utf8') as annotation_test:
            for i in range(1, 3000):
                print i, '-----------------------'
                p = np.random.rand()
                txt = namegen.gen()
                txt = re.sub('\d','',txt)
                pipe_name.txt = txt
                pipe_name.p.reset(jsonObj)
                rs, _, txt = pipe_name.gen()
                if rs is None: continue
                txt = txt.strip()
                txt = unicodeutil.to_vni(txt)
                newwidth = rs.shape[1] * 32.0 / rs.shape[0]
                rs = cv2.resize(rs, (int(newwidth), 32))
                cv2.imwrite(root + str(i) + '.jpg', rs)
                print '@@@'+txt+'@@@'
                cv2.imshow('hihi', rs)
                cv2.waitKey(-1)
                continue
                if i < 2900:
                    annotation_train.write('./' + str(i) + '.jpg ' + txt + '\n')
                else:
                    annotation_test.write('./' + str(i) + '.jpg ' + txt + '\n')

def to_rcnn():
    pass

def gen_compare(sameheight, dsttxt, comparewith):
    dstimg = cv2.imread(comparewith)
    dstimg = np.mean(dstimg, axis=2).astype(np.uint8)
    dstimg_cl = gray2heatmap(dstimg)
    cv2.imshow('dst', resizeToHeight(dstimg, sameheight))
    cv2.imshow('dst-heatmap', resizeToHeight(dstimg_cl, sameheight))
    pipe_name = CMNDPipeName()
    hotengen = HoTenGen(os.path.join(RESOURCE_PATH, 'hovaten.csv'))
    trashgen = Trash(os.path.join(RESOURCE_PATH, 'hovaten.csv'),0.5)
    quanhuyengen = QuanHuyenGen(os.path.join(RESOURCE_PATH, 'tinhtp.csv'), number=2)
    filecontent = codecs.open(TEMPORARY_PATH + '4/aligned.txt', encoding='utf8').read()
    jsonStr = filecontent.replace('\'', '"')
    jsonObj = json.loads(jsonStr)
    namegen = ListGenWithProb([hotengen, quanhuyengen, trashgen], [0.4,0.3,0.3])
    for i in range(1, 3000):
        print i, '-----------------------'
        if dsttxt is not None: 
            pipe_name.txt = dsttxt
        else:
            pipe_name.txt = namegen.gen()
        pipe_name.p.reset(jsonObj)
        rs, _, txt = pipe_name.gen()
        if rs is None: continue
        txt = txt.strip()
        print '@@@'+txt+'@@@'
        rs_cl = gray2heatmap(rs)
        cv2.imshow('gen', resizeToHeight(rs, sameheight))
        cv2.imshow('gen-heatmap', resizeToHeight(rs_cl, sameheight))
        cv2.waitKey(-1)

if __name__ == '__main__':
    to_weinman('/home/loitg/Downloads/images_cmnd_chu/')
#     gen_compare(64, None, '/home/loitg/workspace/genline/resource/samples/by_line/quequantype/tphochiminh2.jpg')
    