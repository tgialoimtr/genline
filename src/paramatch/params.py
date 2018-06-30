'''
Created on Apr 25, 2018

@author: loitg
'''
import random
import numpy as np
import json
from flatten_json import flatten, unflatten
from six import string_types


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
        
        self.uniform_gen_params = {'enable':False, 
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
                                   'std': onethird
                                    }
        self.dummy_gen_params =  {'enable':False, 
                                   'value': 0
                                    }
    
    def __str__(self):
        if self.uniform_gen_params['enable']:
            return str(self.uniform_gen_params['lower']) + ':' + str(self.uniform_gen_params['upper'])
        elif self.gaussian_gen_params['enable']:
            return str(self.gaussian_gen_params['mean']) + '+-' + str(self.gaussian_gen_params['std'])
        elif self.dummy_gen_params['enable']:
            return str(self.dummy_gen_params['value'])
        
        
    def get_x(self):
        if self.uniform_gen_params['enable']:
            return random.uniform(self.uniform_gen_params['lower'], self.uniform_gen_params['upper'])
        if self.gaussian_gen_params['enable']:
            return np.random.normal(self.gaussian_gen_params['mean'], self.gaussian_gen_params['std'], 1)[0]
        if self.dummy_gen_params['enable']:
            return self.dummy_gen_params['value']

    def set_x(self, value):
        raise Exception

    x = property(get_x,set_x)   
    

# class GenerativeParams(object):
#         
#     def __init__(self, jsonStr):
#         self.reset(jsonStr)
#     
#     def reset(self, jsonStr):
#         raw = json.loads(jsonStr)
#         flatten_dict = flatten(raw)
#         for key in flatten_dict:
#             if mode == self.MODE_CHANGING:
#                 mapping = int
#             else:
#                 mapping = 
#             flatten_dict[key] = 
# 
#         if mode == self.MODE_CHANGING:
#             self.changables = unflatten(flatten_dict)
#         else:
#             self.generatives = unflatten(flatten_dict)
#     def represent(self):
#         return '{}'
#     
#     def get(self, key):
#         pass
#     
#     def set(self, key, value):
#         pass

def getKey(args):
    if len(args) == 0:
        return args[0]
    else:
        return '_'.join(args)
    
def checkAndConvert(rawval):
    try:
        ret = float(rawval)
        rettype = float
    except ValueError:
        try:
            ret = int(rawval)
            rettype = int
        except ValueError:
            if isinstance(rawval, string_types):
                return rawval, str
            else:
                raise ValueError
    return ret, rettype

def checkAndConvertObject(rawval):
    try:
        temp,dtype = checkAndConvert(rawval)
        if dtype in [int, float]:
            ret = GenerativeParam()
            ret.dummy_gen_params =  {'enable':True, 
                               'value': temp
                                }
            return ret
    except ValueError:
        pass

    if '+-' in rawval:
        temp = rawval.split('+-')
        assert len(temp) == 2, 'Wrong format, one +- only'
        ret = GenerativeParam()
        ret.gaussian_gen_params =  {'enable':True, 
                           'mean': float(temp[0]),
                           'std': float(temp[1])
                            }
    elif ':' in rawval:
        temp = rawval.split(':')
        assert len(temp) == 2, 'Wrong format'
        ret = GenerativeParam()
        ret.uniform_gen_params =  {'enable':True, 
                           'lower': float(temp[0]),
                           'upper': float(temp[1])
                            }
    else:
        ret = GenerativeParam()
        ret.dummy_gen_params =  {'enable':True, 
                           'value': temp
                            }
    return ret
class GenerativeParams(object):
        
    def __init__(self, jsonStr=None):
        if jsonStr is not None:
            self.reset(jsonStr)
        
    def reset(self, jsonStr):
        if isinstance(jsonStr, string_types):
            raw = json.loads(jsonStr)
        else:
            raw = jsonStr
        self.flat_params = flatten(raw)
        for key in self.flat_params:
            val = checkAndConvertObject(self.flat_params[key])
            self.flat_params[key] = val
        self.params = unflatten(self.flat_params)
    
    def __str__(self):
        ret_dict = {}
        for key in self.flat_params:
            ret_dict[key] = str(self.flat_params[key])
        ret_dict = unflatten(ret_dict)
        return json.dumps(ret_dict, indent=4)
    
    def get(self, *args):
        key = getKey(args)
        if key in self.params:
            ret = self.params[key]
        elif key in self.flat_params:
            ret = self.flat_params[key]
        return ret.x
    
    def getChangable(self):
        ret = {}
        for key, gener in self.flat_params.items():
            ret[key] = gener.x
        return unflatten(ret)
    
    def set(self, *args):
        assert len(args) > 1, 'key,..., value'
        key = getKey(args[:-1])
        val = checkAndConvertObject(args[-1])
        if key in self.params:
            self.params[key] = val
            self.flat_params = flatten(self.params)
        elif key in self.flat_params:
            self.flat_params[key] = val
            self.params = unflatten(self.flat_params)
    
#consider when init: string of list => list; args => object; 
class ChangableParams(object):
        
    def __init__(self, jsonStr=None):
        if jsonStr is not None:
            self.reset(jsonStr)
    
    def reset(self, jsonStr):
        raw = json.loads(jsonStr)
        self.flat_params = flatten(raw)
        for key in self.flat_params:
            val, dtype = checkAndConvert(self.flat_params[key])
            self.flat_params[key] = val
        self.params = unflatten(self.flat_params)

    def __str__(self):
        return json.dumps(self.params, indent=4)
    
    def get(self, *args):
        key = getKey(args)
        if key in self.params:
            ret = self.params[key]
        elif key in self.flat_params:
            ret = self.flat_params[key]
        return ret
    
    def set(self, *args):
        assert len(args) > 1, 'key,..., value'
        key = getKey(args[:-1])
        val, dtype = checkAndConvert(args[-1])
        if key in self.params:
            self.params[key] = val
            self.flat_params = flatten(self.params)
        elif key in self.flat_params:
            self.flat_params[key] = val
            self.params = unflatten(self.flat_params)
    


if __name__ == "__main__":
    cp = ChangableParams()
    gp = GenerativeParams()
    gp.reset(''' {
    "mat-base":"0.7",
    "rel-width" : {"a": "1.2+-0.1", "b":"0.3:0.6" }, 
    "rel-pos-x" : {"ab": 0.01, "VA": -0.03},
    "rel-pos-y" : {"n":"3:6"}
    
    } ''')

    cp.reset(''' {
    "mat-base":"0.7",
    "rel-width" : {"a": 1.2, "b":"-0.3" },
    "rel-pos-x" : {"ab": 0.01, "VA": -0.03},
    "rel-pos-y" : {"n":1.07}
    
    } ''')

    gp.set('rel-pos-y_n', '-6:-3')
    print(gp.get('rel-pos-y_n'))
    print(gp.get('rel-pos-y_n'))
    print(gp.get('rel-pos-y_n'))
    
    cp.set('rel-pos-y','n', -3.4)
    print(cp.get('rel-pos-y','n'))
    print(cp.get('rel-pos-x','VA'))
           
    print(str(cp))
    print(str(gp))
    
     