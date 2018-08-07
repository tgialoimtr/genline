
import os
import sys
import numpy as np

import utils
import model as modellib
from config import Config

DIGITS_CHARSET = "0123456789"
CHARACTERS_CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class TextConfig(Config):
    '''
    Config for training on text dataset
    '''
    #NAME = text
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1  
    #NUM_CLASSES = 1 + 10 # BG + 10 digits
    IMAGE_MIN_DIM = 64
    IMAGE_MAX_DIM = 640
    #IMAGE_PADDING = False
    STEPS_PER_EPOCH = 200 # can change later depend on testing
    RPN_ANCHOR_SCALES = (24, 32, 36, 40, 48)
    TRAIN_ROIS_PER_IMAGE = 200
    VALIDATION_STEPS = 20
    DETECTION_MIN_CONFIDENCE = 0.5
    DETECTION_NMS_THRESHOLD = 0.3


class TextDataset(utils.Dataset):
    
    def load_text(self,dataset_dir,name,charset):
        
        i = 1
        # Add chacracter classes (26 characters)    
        # for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ": 
        # Add digit classes (10 digits)
        # for ch in "0123456789":
        for ch in charset:
            self.add_class(name, i, ch)       
            i += 1
        
        img_dir = os.path.join(dataset_dir,"images")
        mask_dir = os.path.join(dataset_dir,"masks")
        anno_dir = os.path.join(dataset_dir,"annotations")
        textimg_names = [img_name.replace(".jpg","") for img_name in os.listdir(img_dir)]
        for img_name in textimg_names:
            path = os.path.join(img_dir, img_name+".jpg")
            anno_file = open(os.path.join(anno_dir,img_name+".txt"),'r')
            self.add_image(name, image_id=int(img_name), path=path, mask_path=os.path.join(mask_dir,img_name+".npy"), anno=anno_file.read())
            anno_file.close()
        
    def load_mask(self, image_id):
        info = self.image_info[image_id]
        #mask_files = os.listdir(info["mask_path"])
        #mask = []
        #for mask_file in mask_files:
        #    m = int(mask_file.replace(".npy",""))
        #    mask.append(m)
        #mask.sort()
        #mask_files = [np.load(os.path.join(info["mask_path"],str(name)+".npy")).astype(bool).astype(np.uint8) for name in mask]
        #mask = np.stack(mask_files,axis=-1)
        
        mask = np.load(info["mask_path"])
        
        class_ids = []
        anno = info["anno"].replace(' ','')
        for cl in anno:
            for dt in self.class_info:
                if dt["name"]==cl:
                    class_ids.append(dt["id"])
        class_ids = np.array(class_ids, dtype=np.int32)
        
        return mask, class_ids    

    #def image_reference(self): # maybe optional
        
def train(name,charset,train_set,val_set,model=None):
    
    config = TextConfig()
    config.NAME = name
    config.NUM_CLASSES = 1 + len(charset)
    #config.display()
    if not model:
        model = modellib.MaskRCNN(mode="training", config=config, model_dir="logs")
    
    dataset_train = TextDataset()
    dataset_train.load_text(os.path.join(os.getcwd(),train_set),name,charset)
    dataset_train.prepare()
    
    dataset_val = TextDataset()
    dataset_val.load_text(os.path.join(os.getcwd(),val_set),name,charset)
    dataset_val.prepare()
    
    print("Data prepare done")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=100,
                layers='all')
    
if __name__ == '__main__':
    print("start training 1")
    #weights_path = "/home/loitg/training/M-RCNN/Mask_RCNN-2.1/logs/digits20180709T2101/mask_rcnn_digits_0197.h5"
    #config = TextConfig()
    #config.NAME = "digits"
    #config.NUM_CLASSES = 1 + len(DIGITS_CHARSET)
    #model = modellib.MaskRCNN(mode="training", config=config, model_dir="logs")
    #model.load_weights(weights_path, by_name=True)
    train("digits",DIGITS_CHARSET,"id_new_10000","id_new_1000")  
    #dataset_val = TextDataset()
    #dataset_val.load_text(os.path.join(os.getcwd(),"id_1000"),"digit",DIGITS_CHARSET)
    #dataset_val.load_mask(0)
