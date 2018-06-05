'''
Created on Apr 25, 2018

@author: loitg
'''
import random
import numpy as np 


class RangeParam(object):
    def __init__(self, x, paramrange, dtype=float, freeze=False):
        self.range = (float(paramrange[0]), float(paramrange[1]))
        self._x = x
        assert self._x >= self.range[0] and self._x <= self.range[1]
        self.dx = (self.range[1] - self.range[0])/20
        self.dtype = dtype
        self.freeze = freeze
    
    def inc(self):
        if self.freeze: raise NotImplementedError()
        if self._x + self.dx <= self.range[1]:
            self._x += self.dx
        return self.dtype(self._x)
    
    def dec(self):
        if self.freeze: raise NotImplementedError()
        if self._x - self.dx >= self.range[0]:
            self._x -= self.dx
        return self.dtype(self._x)
    def get_x(self):
        return self.dtype(self._x)

    def set_x(self, value):
        if self.freeze: raise NotImplementedError()
        self._x = float(value)

    x = property(get_x,set_x)  
    

class LogParam(object):
    def __init__(self, x, dtype=float, freeze=False):
        self.range = (x/2, x*2)
        self._x = x
        self.dtype = dtype
        self.freeze = freeze
    
    def inc(self):
        if self.freeze: raise NotImplementedError()
        self._x *= 1.1
        return self.dtype(self._x)
    
    def dec(self):
        if self.freeze: raise NotImplementedError()
        self._x /= 1.1
        return self.dtype(self._x)
    def get_x(self):
        return self.dtype(self._x)

    def set_x(self, value):
        if self.freeze: raise NotImplementedError()
        self._x = float(value)

    x = property(get_x,set_x)  

class GenerativeParam(object):
    def __init__(self, dtype=float):
        self.dtype = dtype
        self.values = []
        
        self.uniform_gen_params = {'enable':True, 
                                   'lower':0,
                                   'upper':0
                                   }
        self.gaussian_gen_params = {'enable':False, 
                                    'mean':0,
                                    'std':0}
        
    def snap(self, val):
        self.values.append(val)
     
    def makeDistributor(self):
        if len(self.values) < 1: return
        lower = min(self.values)
        upper = max(self.values)
        middle = sum(self.values)/len(self.values)
        onethird = (upper - lower) * 0.1
        self.uniform_gen_params =  {'enable':True, 
                                   'lower': lower - onethird,
                                   'upper': upper + onethird
                                    }
        self.gaussian_gen_params =  {'enable':False, 
                                   'mean': middle,
                                   'upper': onethird # fix this
                                    }
        
    def get_x(self):
        if self.uniform_gen_params['enable']:
            return random.uniform(self.uniform_gen_params['lower'], self.uniform_gen_params['upper'])
        if self.uniform_gen_params['enable']:
            return np.random.normal(self.uniform_gen_params['mean'], self.uniform_gen_params['std'], 1)[0]

    def set_x(self, value):
        raise Exception

    x = property(get_x,set_x)    