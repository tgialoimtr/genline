'''
Created on Jul 17, 2018

'''

import os
import skimage

from mrcnn.source import model as modellib
from mrcnn.source.config import Config
from mrcnn.source import text
from mrcnn.source import visualize
from cmndgen.datasetgen import datasetgen


class Recognizer(object):
    
    def __init__(self, mode="training", model_dir):
        
        self.mode = mode
        self.model_dir = model_dir
        self.model = None
        self.config = None
        
    def load_model(self, config, mode=None, model_dir=None):
        '''
        Inputs:
            config: specified sub class for the dataset derive from base Config class
            mode: "training" or "inference"
            model_dir: directory to save training logs and trained weights
        '''
        if mode != None:
            self.mode = mode
        if model_dir != None:
            self.model_dir = model_dir
        self.config = config
        self.model = modellib.MaskRCNN(self.mode,self.config,self.model_dir)
        return self.model
    
    def load_weights(self, weights_path):
        '''
        Input: weights_path to h5 file
        '''
        self.model.load_weights(weights_path, by_name=True)
        return self.model
    
    def train_from_data(self,json,data_prop,train_prop):
        '''
        Input: 
            json: params of dataset in .json type
            data_prop: (type, count, data_dir, charset) tuple of dataset's properties
                type: "name" or "id"
                count: int
                data_dir: string of path to save new dataset
                charset: string of character set 
            train_prop: (layers, epochs) tuple of training's properties
                layers: "heads", "3+", "4+", "5+", "all"
                epochs: int
        '''
        type, count, data_dir, charset = data_prop
        layers, epochs = train_prop
        
        # Create train and val datasets
        train_name = type+"_"+str(count)+"_"+self.config.NAME
        datasetgen(type=type, count=count, params=json, datasetname=train_name, save_dir=data_dir)
        val_name = type+"_"+str(round(count/10))+"_"+self.config.NAME
        datasetgen(type=type, count=round(count/10), params=json, datasetname=val_name, save_dir=data_dir)
        
        # Train the model on those datasets
        train_data = text.TextDataset()
        train_data.load_text(os.path.join(data_dir,train_name),self.config.NAME,charset)
        train_data.prepare()
        val_data = text.TextDataset()
        val_data.load_text(os.path.join(data_dir,val_name),self.config.NAME,charset)
        val_data.prepare()
        
        self.model.train(train_data,val_data,
                    learning_rate=self.config.LEARNING_RATE,
                    epochs=epochs,
                    layers=layers)
    
    def recognize_obj(self,image):
        '''
        Input: image in numpy format
        '''
        result = self.model.detect([image],verbose=1)
        
    def recognize_obj_mask(self,image):
        '''
        Input: image in numpy format
        '''
        result = self.model.detect([image],verbose=1)
        r = result[0]
        visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'], 
                            dataset.class_names, r['scores'], ax=ax,
                            title="Predictions")
        