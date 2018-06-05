'''
Created on Jun 5, 2018

@author: loitg
'''
import cv2
import numpy as np
from cmndgen.pipeline import CMNDPipeline

BOARD_NAME = "board"
LINE_NAME = "line"
        
def mergeThenShow(lineName, line, newline):
    #merge 2 lines
    cv2.imshow(newline)

def createControlBoard(boardName, params, updateFunc):

    def click_and_crop(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            pass
            updateFunc()
        elif event == cv2.EVENT_LBUTTONUP:
            pass
            updateFunc()
            
    board = np.ones(1000, 1000, 3)
    for key, val in params.iteritems():
        params[key] = None #update pa
    #add callback to board
    cv2.setMouseCallback(boardName, click_and_crop)
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
        def updateFunc():
            newline = pipeline.gen()
            mergeThenShow(LINE_NAME, line, linenew)
            
        controlboard = createControlBoard(BOARD_NAME, pipeline.params, updateFunc)
        cv2.imshow(BOARD_NAME, controlboard)
        
        
        
        cv2.waitKey(-1)
        
        
        
        
        
        