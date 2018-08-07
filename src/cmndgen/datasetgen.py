'''
Created Jun 27, 2018
'''

import time
import os
import sys
import cv2
import numpy as np

import pipeline as ppl
from textgen.vnnames import HoTenGen

cur_dir = os.getcwd()

a=-0.4; b=0.4; c={}
for i in range(10):
    if i==1: continue
    c['1'+str(i)] = b
    c[str(i)+'1'] = a

paramsID = {
    'id':
    {
        'font':
        {
            'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/9thyssen.ttf',
            'detail-font':
                {'4':'/home/loitg/Downloads/fonts/fontss/cmnd/so_do/OFFSFOW.ttf'},
            'base-height':33,
            'detail-height':{'4':33},
            'base-ratio':{'x':'1.20:1.40','y':1.0},
#                 'detail-ratio':{}
        },
        'relpos':
        {
            'base-relpos-x':0.25,
            'detail-relpos-x': c,
            'relpos-y': {'4':'0.10:0.15'}
        },          
        'x0':'65+-5',
        'y0':'60+-3',
        'height':37,
        'strength':'0.95:1.00'
    },
    'cmnd':
    {
        'font':
        {
            'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_den/UTM HelveBold.ttf',
            'base-height':30,
            'base-ratio':{'x':1.0,'y':1.0}
        },
        'relpos':
        {
            'base-relpos-x':0.05,
            'relpos-y':{}
        },
        'x0':35,
        'y0':25,
        'strength':0.6,
        'height':25
    },             
    'guiso':
    {
        'strength':'0.60:0.80',
        'height':25,
        'amp':1,
        'wavelength':40,
        'length':280,
        'angle':'-0.5:0.5',
        'thick':1,
        'x0':185,
        'y0':50           
    },
    'circle':
    {
        'strength':'0.60:0.80',
        'R1':'92+-3',
        'R2':'102+-3',
        'a1':2,
        'a2':3,
        'n':90, # number on circles
        'thick':1,
        'x0':66,
        'y0':136
    },
    'height':64,
    'width':'350+-10',
    'pad':20,
    'cut':'15:20',
    'strength-bg':'0.2+-0.05',
    'scale':'1.00:1.20',
    'rotate':'0.0:1.5',
    'si_blur': {},
    'si_dot': {},
    'si_blob': {}
    }

paramsName = {
    'name':
    {
        'font':
        {
            'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/chu_in/SP3 - Traveling Typewriter.otf',
            'base-height':33,
            'base-ratio':{'x':1.1,'y':1.0},
        },
        'relpos':
        {
            'base-relpos-x':0.03,
            
            
        },          
        'x0':80,
        'y0':65,
        'height':40,
        'strength':0.95
    },
    'dots':
    {
        'font':
        {
            'base-font':'/home/loitg/Downloads/fonts/fontss/cmnd/so_den/UTM HelveBold.ttf',
            'base-height':30,
            'base-ratio':{'x':1.0,'y':1.0}
        },
        'relpos':
        {
            'base-relpos-x':0.15,
            'relpos-y':{}
        },
        'x0':40,
        'y0':75,
        'strength':1,
        'height':10
    },             
    'guiso':
    {
        'strength':'0.60:0.80',
        'height':20,
        'amp':1,
        'wavelength':40,
        'length':'320:340',
        'angle':0.0,
        'thick':1,
        'x0':200,
        'y0':18            
    },
    'circle':
    {
        'strength':'0.6+-0.05',
        'R1':'87+-3',
        'R2':'102+-3',
        'a1':2,
        'a2':3,
        'n':90, # number on circles
        'thick':1,
        'x0':155,
        'y0':120
    },
    'circle2':
    {
        'strength':'0.5+-0.05',
        'R1':'125+-3',
        'R2':'145+-3',
        'a1':2,
        'a2':3,
        'n':90, # number on circles
        'thick':1,
        'x0':155,
        'y0':120
    },
    'height':64,
    'width':640,
    'pad':20,
    'cut':'15:20',
    'strength-bg':'0.2+-0.05',
    'scale':'1.00:1.20',
    'rotate':'0.0:1.5',
    'si_blur': {},
    'si_dot': {},
    'si_blob': {}
    
    }

def datasetgen(type, count, params, datasetname, save_dir=cur_dir):
    if type == "id":
        pipe_id = ppl.CMNDPipeID()
        txtgen = ppl.RegExGen(r'[0-3]\d{8}')
        #params = paramsID
        
    elif type == "name":
        pipe_id = ppl.CMNDPipeName()
        txtgen = ppl.HoTenGen('/home/loitg/workspace/genline/resource/temp.csv')
        #params = paramsName
    
    else:
        print('Invalid Type')
        return
    
    print("start")
    start = time.time()
    
    set_dir = os.path.join(save_dir, datasetname)
    img_dir = os.path.join(set_dir, "images")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    mask_dir = os.path.join(set_dir, "masks")
    if not os.path.exists(mask_dir):
        os.makedirs(mask_dir)
    anno_dir = os.path.join(set_dir, "annotations")
    if not os.path.exists(anno_dir):
        os.makedirs(anno_dir)
    
    totalgen = 0
    totalimg = 0
    totalmask = 0
    totalanno = 0
    
    for i in range(count):
        pipe_id.p.reset(params)
        pipe_id.txt = txtgen.gen()
        
        gentime = time.time()
        grayimg, mask_chars, text = pipe_id.gen()
        totalgen += (time.time() - gentime)
        
        imgtime = time.time()
        img_path = os.path.join(img_dir, str(i).zfill(len(str(count)))+".jpg")
        cv2.imwrite(str(img_path), grayimg)
        totalimg += (time.time() - imgtime)
        
        masktime = time.time()
        mask = np.stack(mask_chars,axis=-1)
        mask_path = os.path.join(mask_dir, str(i).zfill(len(str(count)))+".npy")
        np.save(mask_path, mask)
        totalmask += (time.time() - masktime)
        
        annotime = time.time()
        anno_file = open(anno_dir+"/"+str(i).zfill(len(str(count)))+".txt",'w')
        anno_file.write(text)
        anno_file.close()
        totalanno += (time.time() - annotime)
        print("Created {} lines in {} seconds".format(i,round(time.time() - start)),end="\r")
    
    cv2.waitKey(0)
    print("Created {} lines in {} seconds".format(count,round(time.time() - start)))
    print("Average gen time:",totalgen/count)
    print("Average img time:",totalimg/count)
    print("Average mask time:",totalmask/count)
    print("Average anno time:",totalanno/count)
    print("Average gen one img time:",(totalgen+totalimg+totalmask+totalanno)/count)
    
if __name__ == '__main__':
    datasetgen(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
    #start = time.time()
    #a = ppl.HoTenGen('/home/loitg/workspace/genline/resource/temp.csv')           
    #for i in range(100000):
    #    print(a.gen(),end="\r")
    #print(time.time() - start)          
               
#end        
               