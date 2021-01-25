from pathlib import Path

import cv2
import gdal
import numpy as np

class OutOfBorder(Exception): pass

class _Image:
    def __init__(self, filename, info=None):
        filename = Path(filename)
        self.filename = 'imgs' / filename
        self.info = info
        self._base_zoom_level = 6
        self._base_tile_side = 256
        self.buffer = np.zeros((self._base_tile_side,self._base_tile_side,3)).astype(np.uint8) 

    def convert_tile_idx(self, x,y,z):
        # returns (x0,x1),(y0,y1) px coordinates of that tile
        p = max(0, self._base_zoom_level - z)
        crop_side = int(self._base_tile_side * 2**p)
        x = int((x)*crop_side)
        y = int((y)*crop_side)
        w,h = crop_side, crop_side 
        return (x,y), (w,h), 2**p

    def blank_tile(self, filler=0):
        self.buffer.fill(filler)
        return self.buffer

    def zero_tile(self):
        return np.zeros((1,1)).astype(np.uint8)

    def resize(self, block, scale):
        h, w = block.shape[:2]
        size = (self._base_tile_side, self._base_tile_side)
        if h == w: return cv2.resize(block, size, cv2.INTER_AREA)
        
        a,b = h//scale, w//scale
        block = cv2.resize(block, (b,a), cv2.INTER_AREA)
        hh, ww = block.shape[:2]
        t = self.blank_tile(127)
        t[:hh,:ww,:] = block
        return t

    def read_part(self):
        raise NotImplementedError


class BigImage(_Image):
    def set_tile(self, x, y, zoom):
       self.x, self.y, self.z = x,y,zoom
       self.file = gdal.Open(str(self.filename), gdal.GA_ReadOnly)
       self.dims = [self.file.RasterXSize, self.file.RasterYSize]
       
    def __call__(self):
        return self.read_part()

    def check_borders(self, x,y,w,h, W,H):
        if x<0 or y<0 or x>W or y>H: raise OutOfBorder
        w = min(w, W-x)
        h = min(h, H-y)
        return (x,y), (w,h)

    def read_part(self):
        # called (in mp) after set_tile
        (x,y), (w,h), scale = self.convert_tile_idx(self.x, self.y, self.z)
        try:
            (x,y), (w,h) = self.check_borders(x,y,w,h,*self.dims)
        except OutOfBorder:
            return self.zero_tile()

        block = self.file.ReadAsArray(xoff=x, yoff=y, xsize=w, ysize=h)
        del self.file 
        block = block.transpose(1,2,0)
        block = self.resize(block, scale)
        return block


class ImageFolder:
    def __init__(self, filename):
        self.filename = filename

    def set_tile(self, x, y, zoom):
        pass

    def __call__(self):
        return (np.random.random((256,256,3))*255).astype(np.uint8)
