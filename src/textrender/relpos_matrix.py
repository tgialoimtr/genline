'''
Created on Jun 5, 2018

@author: loitg
'''

class RelInfo(object):
    def __init__(self, hor=0.0, ver=0.0):
        self.hor = hor
        self.ver = ver
        
        
class RelPosSimple(object):

    def __init__(self):
        self.mat = RelInfo()
    
    def at(self, chars):
        (beforeChar, afterChar) = chars
        return self.mat

   
class RelPos4D(object):

    def __init__(self, charset, hor=0.0, ver=0.0, bodau=None):
        self.charset = charset
#         self.charset2index = {}
#         for i, c in enumerate(self.charset):
#             self.charset2index[c] = i
        self.mat = {}
        self.bodau = bodau
        for c1 in self.charset:
            for c2 in self.charset:
                self.mat[(c1, c2)] = RelInfo(hor=hor, ver=ver)
        
    def at(self, chars):
        (beforeChar, afterChar) = chars
        if self.bodau:
            beforeChar = self.bodau(beforeChar)
            afterChar = self.bodau(afterChar)
        return self.mat[(beforeChar, afterChar)]
    
    