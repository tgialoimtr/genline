'''
Created on Jun 5, 2018

@author: loitg
'''
import cv2
import numpy as np
from cmndgen.pipeline import CMNDPipeline

def createControlBoard(params):
    board = np.ones(1000, 1000, 3)
    #add callback to board
    
    return board

if __name__ == '__main__':
    lines = []
    for line in lines:
        txt = raw_input('ground truth text: ')
        
        
        pipeline = CMNDPipeline()
        # add font
        # init Scale Param
        pipeline.initParams()
        # show image with callback to edit another image, dynamic change text ... hum
        controlboard = createControlBoard(pipeline.params)
        cv2.imshow('board', controlboard)
        
        