import os
import sys
from pathlib import Path

import torch
        
import cv2
import numpy as np

class Inferencer:
    
    def __init__(self, gpus='0', threshold=0.5, root='/root/infer/model'):
        self.threshold = float(threshold)
        os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
        os.environ['CUDA_VISIBLE_DEVICES']=gpus
        sys.path.append(root + '/src')
        from infer import get_infer_func
        self.infer_func = get_infer_func(root)

    def inference(self, img):
        # HWC
        img = img.transpose(2,0,1)
        out = self.infer_func([img])
        out = out.squeeze().cpu().numpy()
        torch.cuda.empty_cache()
        
        #out = cv2.resize(out, (H,W))
        # Segmentation map generally will not have same dimensions as input. Can be daownscaled
        # Leaflet will resize mask into shape anyway       

        out = out > self.threshold
        out = (out * 255.).astype(np.uint8)
        out = np.expand_dims(out, -1).repeat(4,-1) # 4 for RGBA
        out[...,0] = 0 
        out[...,1] = 255 # All in one channel
        out[...,2] = 0
        return out












