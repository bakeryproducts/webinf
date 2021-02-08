from pathlib import Path

import cv2
import gdal
import numpy as np

import rasterio

class OutOfBorder(Exception): pass

class _Image:
    def __init__(self, filename, info=None):
        filename = Path(filename)
        self.filename = filename
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
        if h == w: return cv2.resize(block, size, cv2.INTER_NEAREST)
        
        a,b = h//scale, w//scale
        block = cv2.resize(block, (b,a), cv2.INTER_NEAREST)
        hh, ww = block.shape[:2]
        t = self.blank_tile(127)
        t[:hh,:ww,:] = block
        return t



class BigImage(_Image):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataset = rasterio.open(self.filename)
        self.dims = self.dataset.width, self.dataset.height
        self.bands = list(range(1, 1+self.dataset.count))

    def check_borders(self, x,y,w,h, W,H):
        if x<0 or y<0 or x>W or y>H: raise OutOfBorder
        w = min(w, W-x)
        h = min(h, H-y)
        return (x,y), (w,h)

    def _read_from_raster(self, x,y,w,h):
        block = self.dataset.read(self.bands, window=((y,y+h),(x,x+w)))  
        print(block.shape, self.bands)
        if self.bands == [1]: 
            block*=255
            block = block.repeat(3,0)
        return block 

    def read_image_part(self, l_tile, t_tile, r_tile, b_tile, zoom):
        (l, t), _, _ = self.convert_tile_idx(l_tile, t_tile, zoom)
        (r0, b0), (w,h), _ = self.convert_tile_idx(r_tile, b_tile, zoom)
        r, b = r0+w, b0+h
        block = self._read_from_raster(l,t, r-l, b-t)
        block = block.transpose(1,2,0)
        return block

    def read_tile(self, x_tile, y_tile, zoom):
        # called (in mp) after set_tile
        (x,y), (w,h), scale = self.convert_tile_idx(x_tile, y_tile, zoom)
        try:
            (x,y), (w,h) = self.check_borders(x,y,w,h,*self.dims)
        except OutOfBorder:
            return self.zero_tile()

        block = self._read_from_raster(x,y,w,h)
        del self.dataset 
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
