'''
Created on Jun 5, 2018

@author: loitg
'''

from char import CharFont

class Font(object):

    def __init__(self):
        pass
    
    
    

class HandWritten(Font):

    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    
    
class Printed(Font):

    def __init__(self, charset):
        self.infos = {}
        for c in charset:
            self.infos[c] = CharFont()
        pass  