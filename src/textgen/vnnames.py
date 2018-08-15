# -*- coding: utf-8 -*-
'''
Created on Jul 5, 2018

@author: loitg
'''
import random
import numpy as np
import pandas as pd
from textgen.combiner import RegExGen
from utils.common import RESOURCE_PATH

def quan(qh):
    rs = qh
    space = u' ' if np.random.rand() < 0.5 else u''
    if np.random.rand() < 0.5: rs = rs.replace(u'Thi xã', u'Thị trấn')
    if np.random.rand() < 0.7:
        rs = rs.replace(u'Quận ', u'Q.'+space) if np.random.rand() < 0.5  else rs.replace(u'Quận ', u'')
        rs = rs.replace(u'Huyện ', u'H.'+space) if np.random.rand() < 0.5  else rs.replace(u'Huyện ', u'')
        rs = rs.replace(u'Thi xã ', u'TX.'+space) if np.random.rand() < 0.5  else rs.replace(u'Thi xã ', u'')
        rs = rs.replace(u'Thi trấn ', u'TT.'+space) if np.random.rand() < 0.5  else rs.replace(u'Thi xtrấn ', u'')
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

class Trash(object):  
    def __init__(self, csvfilepath, meaningless):
        self.data = pd.read_csv(csvfilepath, encoding='utf-8')
        self.fullnames = self.data['ho va ten'].values
        self.sep = RegExGen('[ ]?,[ ]')
        self.meaningless = meaningless
        
    def gen(self):    
        temp = np.random.choice(self.fullnames,2)
        temp1 = temp[0].strip().split(' ')[-random.randint(1,2):]
        temp2 = temp[1].strip().split(' ')[-random.randint(1,2):]
        temp1 = ' '.join([x.lower() if np.random.rand() < 0.5  else x.capitalize() for x in temp1])
        temp2 = ' '.join([x.lower() if np.random.rand() < 0.5  else x.capitalize() for x in temp2])
        if np.random.rand() < self.meaningless:
            return u''.join(random.sample(temp1 + temp2,len(temp1 + temp2)))
        else:
            return temp1 + self.sep.gen() + temp2
    
    
    
class QuanHuyenGen(object):
    
    def __init__(self, csvfilepath, number=1):
        self.tinhtp = pd.read_csv(csvfilepath, encoding='utf-8')
        self.number = number
        self.sep = RegExGen('[ ]?,[ ]')
        
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
    gener = QuanHuyenGen(RESOURCE_PATH + 'tinhtp.csv')
#     gener = HoTenGen(RESOURCE_PATH + 'temp.csv')
    
    for i in range(10):
        txt = gener.gen()
        print(txt)
    
