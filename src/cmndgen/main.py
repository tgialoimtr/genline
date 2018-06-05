'''
Created on Mar 17, 2018

@author: loitg
'''

import cv2
import os, sys
import random
import numpy as np

from paramatch.collections import Params
from cmndgen.cmndgenline import Stack
        
if __name__ == '__main__': 

    #load Generatives if saved
    savedpath = '/home/loitg/Downloads/cmnd_aia/params.pkl'
    if os.path.isfile(savedpath):
        paramMgr = Params.load(savedpath)  
    else:
        paramMgr = Params()
    cmndgen = Stack(550,80, paramMgr)
#     img = cmndgen.genIDDen()
#     #genShortKey
#     desc = paramMgr.genShortKeys()
#     # TUNE/CHANGING pocess:
#     while(True):
#         print(desc)
#         #updateFromUser
#         k = raw_input('Select Param: ')
#         inc = k.isupper()
#         k = k.lower()
#         paramMgr.updateFromUser(k, inc)
#         #apply and show 
#         img, txt = cmndgen.genIDDen()
#         cv2.imshow('hihi', img)
#         cv2.waitKey(300)
#         if k == '1':
#             paramMgr.snapShot()
#         elif k == '2':
#             break
#                    
#     paramMgr.save(savedpath)
#            
#     sys.exit(0)  
         
    
        
     
    # GEN process:
    paramMgr.startGenerative()          
            
            
    root = '/home/loitg/Downloads/images_txt/'
    paramMgr.startGenerative() 
    with open(root + 'anno-train.txt', 'a') as annotation_train:
        with open(root + 'anno-test.txt', 'a') as annotation_test:
            for i in range(1, 300000):
                print i, '-----------------------'
                cmndgen.width = random.randint(560, 640)
                p = np.random.rand()
                if p < 0.4:
                    rs, txt = cmndgen.genID()
                elif p < 0.6:
                    rs, txt = cmndgen.genIDDen()
                else:
                    rs, txt = cmndgen.genDOB()
                if rs is None: continue
                txt = txt.strip()
                newwidth = rs.shape[1] * 32.0 / rs.shape[0]
                rs = cv2.resize(rs, (int(newwidth), 32))
                cv2.imwrite(root + str(i) + '.jpg', rs)
#                 print '@@@'+txt+'@@@'
#                 cv2.imshow('hihi', rs)
#                 cv2.waitKey(-1)
                
                continue
                
                if i < 295000:
                    annotation_train.write('./' + str(i) + '.jpg ' + txt + '\n')
                else:
                    annotation_test.write('./' + str(i) + '.jpg ' + txt + '\n')
        
        

    
        
    
