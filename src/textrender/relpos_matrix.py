'''
Created on Jun 5, 2018

@author: loitg
'''

class RelInfo(object):
    def __init__(self):
        self.hor = 0.0
        self.ver = 0.0
        
        
class RelPosSimple(object):

    def __init__(self):
        self.mat = RelInfo()
    
    def at(self, (beforeChar, afterChar)):
        return self.mat

   
class RelPos4D(object):

    def __init__(self, charset):
        self.charset = charset
#         self.charset2index = {}
#         for i, c in enumerate(self.charset):
#             self.charset2index[c] = i
        self.mat = {}
        for c1 in self.charset:
            for c2 in self.charset:
                self.mat[(c1, c2)] = RelInfo()
        
    def at(self, (beforeChar, afterChar)):
        return self.mat[(beforeChar, afterChar)]
    
    