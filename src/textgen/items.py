'''
Created on Jan 17, 2018

@author: loitg
'''
import re
import numpy as np
import rstr





class Gen(object):
    '''
    Genner base class
    '''

    def __init__(self):
        '''
        Constructor
        '''
   
    def gen(self):
        return ''
 
    
class RegExGen(Gen):
    
    def __init__(self,expr):
        self.expr = expr
    
    
    def gen(self):
        return rstr.xeger(self.expr)




class StringGen(Gen): 
    
    def __init__(self, initstr):
        self.string = initstr
    
    def gen(self):
        return self.string


class StringListGen(Gen): 
    
    def __init__(self, strlist):
        self.strlist = strlist
    
    def gen(self):
        selected = self.strlist[int(np.random.randint(0, len(self.strlist)))]
        return selected

    
class SepGen(object):
    def __init__(self, sep, allowFar=True, allowBlank=False):
        self.sep = sep
        self.sepreg = r'[ ]?' + re.escape(sep)
        if allowBlank:
            self.sepreg += r'?'
        if allowFar:
            self.sepreg += r'([ ]?|[ ]{0,10})'
        else:
            self.sepreg += r'[ ]?'
        
    def gen(self):
        sep = rstr.xeger(self.sepreg)
        if len(sep) == 0: sep = self.sep
        if np.random.rand(1) < 0.5:
            return sep
        else:
            return sep[::-1]
        
        
if __name__ == '__main__':
    g = StringListGen(['a','\s\\k','bpopp'])
    for i in range(20):
        print '----'+g.gen()+'------'
            
            
        