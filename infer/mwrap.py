import os
import sys
from pathlib import Path

import torch
        
import cv2
import numpy as np

class Inferencer:
    
    def __init__(self, gpus='3', threshold=0.5, root='/root/infer/model'):
        self.threshold = threshold
        os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
        os.environ['CUDA_VISIBLE_DEVICES']=gpus
        sys.path.append(root + '/src')
        
        from config import cfg, cfg_init
        from model import load_model
        from augs import get_aug

        cfg_init(root + '/cfg.yaml')
        cfg.defrost()
        cfg.PARALLEL.LOCAL_RANK=0
        cfg.PARALLEL.DDP=False
        aa = get_aug('val', cfg['TRANSFORMERS'], using_boxes=False)
        self.normalize  = aa.transforms[1].transforms[0]

        model_name = list(Path(root + '/models/').glob('*.pth'))[0]
        self.model  = load_model(cfg, model_name).cuda()
        self.model.eval()

    def inference(self, img):
        W,H = img.shape[:2]
        img = self.normalize(image=img)['image']
        img = np.expand_dims(img.transpose((2,0,1)),0)
        img = torch.from_numpy(img).cuda()
        
        with torch.no_grad():
            out = self.model(img)[0,0]
            out.sigmoid_()
            out = out.cpu().numpy()
        del img
        torch.cuda.empty_cache()
        
        #out = cv2.resize(out, (H,W))
        # Segmentation map will not have same dimensions as input. Can be daownscaled
        # Leaflet will resize mask into shape anyway       

        out = out > self.threshold
        out = (out * 255.).astype(np.uint8)
        out = np.expand_dims(out, -1).repeat(4,-1) # 4 for RGBA
        out[...,1:-1] = 0
        out[...,0] = 255 # All red in first channel of mask
        return out












