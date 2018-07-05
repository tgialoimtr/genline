# -*- coding: utf-8 -*-
'''
Created on Jul 5, 2018

@author: loitg
'''
import random
import numpy as np
import pandas as pd
from textgen.combiner import RegExGen

def quan(qh):
    rs = qh
    space = u' ' if np.random.rand() < 0.5 else u''
    if np.random.rand() < 0.7:
        rs = rs.replace(u'Quận ', u'Q.'+space) if np.random.rand() < 0.5  else rs.replace(u'Quận ', u'')
        rs = rs.replace(u'Huyện ', u'H.'+space) if np.random.rand() < 0.5  else rs.replace(u'Huyện ', u'')
        rs = rs.replace(u'Thi xã ', u'TX.'+space) if np.random.rand() < 0.5  else rs.replace(u'Thi xã ', u'')
        rs = rs.replace(u'Thành phố ', u'TP.'+space) if np.random.rand() < 0.5  else rs.replace(u'Thành phố ', u'')
    return rs

def tinh(tt):
    rs = tt
    space = u' ' if np.random.rand() < 0.5 else u''
    if np.random.rand() < 0.7:
        rs = rs.replace(u'Thành phố ', u'TP.'+space) if np.random.rand() < 0.5  else rs.replace(u'Thành phố ', u'')
        rs = rs.replace(u'Tỉnh'+space, u'')
    return rs   


class HoTenGen(object):


    def __init__(self, csvfilepath):
        self.data = pd.read_csv(csvfilepath, encoding='utf-8')
        self.fullnames = self.data['ho va ten'].values
        
    def gen(self):    
        temp = np.random.choice(self.fullnames, 2)
        hogen = temp[0].strip().split(' ')[:random.randint(1,2)]
        hogen = ' '.join([x.upper() for x in hogen])
        tengen = temp[1].strip().split(' ')[-random.randint(1,2):]
        tengen = ' '.join([x.upper() for x in tengen])
        return hogen + ' ' + tengen
        

class QuanHuyenGen(object):
    
    def __init__(self, csvfilepath, number=1):
        self.tinhtp = pd.read_csv(csvfilepath, encoding='utf-8')
        self.number = number
        self.sep = RegExGen('[ ]?,[ ]?')
        
    def gen(self):
        if self.number < 2:
            row = self.tinhtp.sample(1)
            if np.random.rand() < 0.5:
                a = quan(row['quanhuyen'].iloc[0])
                return a
            else:
                b = tinh(row['tinhtp'].iloc[0])
                return b
        if self.number < 3:
            row = self.tinhtp.sample(1)
            a = quan(row['quanhuyen'].iloc[0])
            b = tinh(row['tinhtp'].iloc[0])
            return a + self.sep.gen() + b
        else:
            raise ValueError('unsupport number')

if __name__ == '__main__':
    gener = QuanHuyenGen('/home/loitg/workspace/genline/resource/tinhtp.csv')
#     gener = HoTenGen('/home/loitg/workspace/genline/resource/temp.csv')
    
    for i in range(10):
        txt = gener.gen()
        print(txt)
    
