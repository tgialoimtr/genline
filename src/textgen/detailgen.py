'''
Created on Jan 17, 2018

@author: loitg
'''
import numpy as np
from items import StringListGen, Gen
from faker import Faker
import re
import random
from textgen.combiner import ListGenWithProb
import rstr
from datetime import datetime


def replaceZeroWithProb(oridatetime, replaceProb=0.5):
    if np.random.rand() < replaceProb:
        result = re.sub(r'0(\d\D)', r'\1', oridatetime)
        return result
    else:
        return oridatetime

def unicode2ascii(text):
    ret = ''.join(i for i in text if ord(i)<128)
    return ret.encode('utf-8')

def changeCaseWithProb(sentence, upper=0.5, lower=0.25): #Capitalize = 1.0 - upper - lower
    p = np.random.rand()
    if upper > p:
        return sentence.upper()
    elif upper + lower > p:
        return sentence.lower()
    else:
        l = [w.capitalize() for w in sentence.split(' ')]
        return ' '.join(l)

class ChangeCaseGen(Gen):
    
    def __init__(self, basegen, upper=0.5, lower=0.25): #Capitalize = 1.0 - upper - lower
        self.basegen = basegen
        self.upper = upper
        self.lower = lower
    
    def gen(self):
        return changeCaseWithProb(self.basegen.gen(), self.upper, self.lower)

class CL0Gen(Gen):
    def __init__(self):
        self.faker = Faker()
        self.dateformat = "%d%m%y"
        self.timeformat = "%H:%M:%S"
        self.c0 = "[ ]\d{5}[ ]\d{4}[ ]"
        self.c1 = "[ ]\d{4}[ ][A-Za-z]{2,5}"
        
    def gen(self):
        d = self.faker.future_date(end_date="+350d")
        d = d.strftime(self.dateformat)
        t = self.faker.time(pattern=self.timeformat, end_datetime=None)
        return rstr.xeger(d+self.c0+t+self.c1)
    
    
class DateGen(Gen):
    '''
    Date
    '''
    def __init__(self, fromdate = None, todate = None, dateformat = None):
        '''
        Constructor
        '''
        self.faker = Faker('en_US')
        self.dateformat = ListGenWithProb(*dateformat)
        if fromdate is not None:
            self.fromdate = datetime.strptime(fromdate, "%Y-%m-%d")
        else:
            self.fromdate = datetime.now()
        if todate is not None:
            self.todate = datetime.strptime(todate, "%Y-%m-%d")
        else:
            self.todate = datetime.now()
        
    def gen(self):
#         d = self.faker.date_between(start_date="-365d", end_date="-60d")
        d = self.faker.date_time_between_dates(datetime_start=self.fromdate, datetime_end=self.todate, tzinfo=None).date()
        fm = self.dateformat.gen()
        d = d.strftime(fm)
        d = replaceZeroWithProb(d, 0.15)
        d = changeCaseWithProb(d, upper=0.5, lower=0.0)
        return d


class TimeGen(Gen):
    '''
    Time
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.faker = Faker()
        self.dateformat = ListGenWithProb(["%H:%M(:%S)?","%I:%M(:%S)[ ]?%p"],[0.5,0.5])

        
    def gen(self):
        fm = self.dateformat.gen()
        t = self.faker.time(pattern=fm, end_datetime=None)
        d = replaceZeroWithProb(t)
        d = changeCaseWithProb(d, upper=0.5, lower=0.1)
        return d


   
class StoreGen(Gen): 
    
    def __init__(self, storelistpath):
        f = open(storelistpath, 'r')
        self.storeset = set()
        for line in f:
            temp = unicode2ascii(line).strip()
            if len(temp) > 4:
                self.storeset.add(temp)

    def gen(self):
        storestr = random.sample(self.storeset, 1)[0]
        storewords = storestr.split(' ')
        if len(storewords) > 2:
            pos = np.random.randint(len(storewords)-1)
            rs = storewords[pos] + ' ' + storewords[pos+1]
        else:
            rs = storestr
        return changeCaseWithProb(rs, upper=0.75, lower=0.0)


class NameGen(Gen):
    
    def __init__(self):
        self.faker = Faker()
    def gen(self):
        return self.faker.name()
    
    
class ParragraphGen(Gen): 
    
    def __init__(self, dictpath, numword=2):
        f = open(dictpath, 'r')
        self.wordset = set()
        self.numword = numword
        temp = set()
        for line in f:
            temp.update(set(line.split(' ')))
        for w in temp:
            w = w.strip()
            if len(w) > 0:
                self.wordset.add(w)
    
    def gen(self):
        words = random.sample(self.wordset, self.numword)
        return ' '.join(words)
    
          
if __name__ == '__main__':
#     g = ParragraphGen('/home/loitg/workspace/genreceipt/resource/parragraph.txt')
    g = DateGen(fromdate='2018-01-01', dateformat=(["%d-%m-%Y"], [1.1]))
    for i in range(200):
        print '----'+g.gen()+'------'
            
            
        
