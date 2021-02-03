import sys

import cv2
import numpy as np
import torch
sys.path.append('/root/infer/model/src')

import os
os.environ['CUDA_VISIBLE_DEVICES']='3'

from config import cfg, cfg_init
from model import build_model
from augs import get_aug



cfg_init('/root/infer/model/cfg.yaml')
cfg.defrost()
cfg.PARALLEL.LOCAL_RANK=0
cfg.PARALLEL.DDP=False
aa = get_aug('val', cfg['TRANSFORMERS'], using_boxes=False)
normalize  = aa.transforms[1].transforms[0]

model, opt  = build_model(cfg)

def inference(inp):
    print("INFERENCE\n\n")
    print(inp.shape)

    inp = normalize(image=inp)['image']
    print(inp.mean(), inp.std())
    inp = inp.reshape(1,3,inp.shape[0], inp.shape[1])
    inp = torch.from_numpy(inp).cuda()
    print(inp.shape)

    model.eval=True
    with torch.no_grad():
        out = model(inp)[0,0]
        out = torch.sigmoid(out).cpu().numpy()
    
    print(out.shape)
    out = cv2.resize(out, inp.shape[2:][::-1])
    out = np.expand_dims(out, -1).repeat(3,-1)# 4 RGBA
    print(out.shape, out.dtype)
    out = (out * 255.).astype(np.uint8)
    return out












