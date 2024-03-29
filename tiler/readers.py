import json
from pathlib import Path

import cv2
# import gdal
from osgeo import gdal
import slideio
import numpy as np
import pandas as pd

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

    def resize(self, block, scale, border_tile=False):
        h, w = block.shape[:2]
        size = (self._base_tile_side, self._base_tile_side)
        if h == w and not border_tile: return cv2.resize(block, size, cv2.INTER_NEAREST)

        a,b = h//scale, w//scale
        block = cv2.resize(block, (b,a), cv2.INTER_NEAREST)
        hh, ww = block.shape[:2]
        t = self.blank_tile(127)
        t[:hh,:ww,:] = block
        return t


class SmallImage(_Image):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataset = cv2.imread(str(self.filename))  # HWC
        self.dims = self.dataset.shape[1], self.dataset.shape[0],
        self.bands = list(range(1, 1 + self.dataset.shape[-1]))

    def check_borders(self, x, y, w, h, W, H):
        if x < 0 or y < 0 or x >= W or y >= H: raise OutOfBorder
        w = min(w, W - x)
        h = min(h, H - y)
        return (x, y), (w, h)

    def _read_from_raster(self, x, y, w, h):
        #block = self.dataset.read(self.bands, window=((y,y+h),(x,x+w)))
        block = self.dataset[y:y + h, x:x + w, :]
        if self.bands == [1]:
            block *= 255
            block = block.repeat(3, -1)
        return block

    def read_image_part(self, l_tile, t_tile, r_tile, b_tile, zoom):
        (l, t), _, _ = self.convert_tile_idx(l_tile, t_tile, zoom)
        (r0, b0), (w, h), _ = self.convert_tile_idx(r_tile, b_tile, zoom)
        r, b = r0 + w, b0 + h
        block = self._read_from_raster(l, t, r - l, b - t)
        block = cv2.cvtColor(block, cv2.COLOR_BGR2RGB)
        return block

    def read_tile(self, x_tile, y_tile, zoom):
        # called (in mp) after set_tile
        border_tile = False
        (x,y), (w,h), scale = self.convert_tile_idx(x_tile, y_tile, zoom)
        try:
            (x, y), (cliped_w, cliped_h) = self.check_borders(x,y,w,h,*self.dims)
            if w != cliped_w or h != cliped_h: border_tile = True
        except OutOfBorder:
            return self.zero_tile()

        block = self._read_from_raster(x,y,w,h)
        block = cv2.cvtColor(block, cv2.COLOR_BGR2RGB)
        block = self.resize(block, scale, border_tile)
        return block


class SVSImage(_Image):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # image = scene.read_block(size=(size,0))
        slide = slideio.open_slide(str(self.filename), 'SVS')
        self.dataset = slide.get_scene(0)
        self.dims = self.dataset.size #self.dataset.width, self.dataset.height
        # self.bands = list(range(1, 1 + self.dataset.count))

    def check_borders(self, x,y,w,h, W,H):
        if x < 0 or y < 0 or x > W or y > H: raise OutOfBorder
        w = min(w, W - x)
        h = min(h, H - y)
        return (x,y), (w,h)

    def _read_from_raster(self, x,y,w,h):
        # block = self.dataset.read(self.bands, window=((y,y+h),(x,x+w)))
        block = self.dataset.read_block(rect=(x,y,w,h)) # rect x,y,w,h
        if len(block.shape) == 3:
            a,b,c = block.shape
            if a == 1 or a == 3: # CHW
                block = block.transpose(1,2,0)
            a,b,c = block.shape
            if c == 1:
                block = block.repeat(3, -1)
        elif len(block.shape) == 2:
            block = np.expand_dims(block, -1).repeat(3, -1)

        print(block.shape, block.dtype, block.max())
        return block # HwC

    def read_image_part(self, l_tile, t_tile, r_tile, b_tile, zoom):
        (l, t), _, _ = self.convert_tile_idx(l_tile, t_tile, zoom)
        (r0, b0), (w,h), _ = self.convert_tile_idx(r_tile, b_tile, zoom)
        r, b = r0 + w, b0 + h
        block = self._read_from_raster(l,t, r-l, b-t)
        return block

    def read_tile(self, x_tile, y_tile, zoom):
        # called (in mp) after set_tile
        border_tile = False
        (x,y), (w,h), scale = self.convert_tile_idx(x_tile, y_tile, zoom)
        try:
            (x, y), (cliped_w, cliped_h) = self.check_borders(x,y,w,h,*self.dims)
            if w != cliped_w or h != cliped_h: border_tile = True
        except OutOfBorder:
            return self.zero_tile()

        block = self._read_from_raster(x,y,w,h)
        block = self.resize(block, scale, border_tile)
        print("\t\t\tTILE:", block.shape, block.dtype)
        if block.dtype == np.uint16:
            block = block / 65535 * 255
            block = block.astype(np.uint8)
        return block


class BigImage(_Image):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataset = rasterio.open(self.filename)
        self.dims = self.dataset.width, self.dataset.height
        self.bands = list(range(1, 1 + self.dataset.count))

    def check_borders(self, x,y,w,h, W,H):
        if x < 0 or y < 0 or x > W or y > H: raise OutOfBorder
        w = min(w, W - x)
        h = min(h, H - y)
        return (x,y), (w,h)

    def _read_from_raster(self, x,y,w,h):
        block = self.dataset.read(self.bands, window=((y,y+h),(x,x+w)))
        print(block.shape, self.bands, block.max())

        if len(block.shape) == 3:
            a,b,c = block.shape
            if a == 1 or a == 3: # CHW
                block = block.transpose(1,2,0)
            a,b,c = block.shape
            if c == 1:
                block = block.repeat(3, -1)
        elif len(block.shape) == 2:
            block = np.expand_dims(block, -1).repeat(3, -1)

        print(block.shape, block.dtype, block.max())
        # if self.bands == [1]:
        #     block *= 255
        #     block = block.repeat(3,0)
        return block

    def read_image_part(self, l_tile, t_tile, r_tile, b_tile, zoom):
        (l, t), _, _ = self.convert_tile_idx(l_tile, t_tile, zoom)
        (r0, b0), (w,h), _ = self.convert_tile_idx(r_tile, b_tile, zoom)
        r, b = r0 + w, b0 + h
        block = self._read_from_raster(l,t, r-l, b-t)
        return block

    def read_tile(self, x_tile, y_tile, zoom):
        # called (in mp) after set_tile
        border_tile = False
        (x,y), (w,h), scale = self.convert_tile_idx(x_tile, y_tile, zoom)
        try:
            (x, y), (cliped_w, cliped_h) = self.check_borders(x,y,w,h,*self.dims)
            if w != cliped_w or h != cliped_h: border_tile = True
        except OutOfBorder:
            return self.zero_tile()

        block = self._read_from_raster(x,y,w,h)
        self.dataset.close()
        del self.dataset
        block = self.resize(block, scale, border_tile)
        print("\t\t\tTILE:", block.shape, block.dtype)
        if block.dtype == np.uint16:
            block = block / 65535 * 255
            block = block.astype(np.uint8)
        return block


class JsonReader:
    def __init__(self, filename, prefix):
        self.filename = filename
        self.prefix = prefix
        self.matr = self.create_matr(filename)

    def create_matr(self, filename):
        with open(str(filename), 'r') as f:
            data = json.load(f)

        df = pd.read_csv(str(filename.parent / data['proj']))
        x_size = df['x'].max()
        s = np.zeros((x_size+1, x_size+1), dtype=np.object_)

        data_path = Path(data.get('data_path', ''))
        for i,r in df.iterrows():
            s[r['x']][r['y']] = str(data_path / r['fn'])
        return s

    def get_img_from_xyz(self, x,y, zoom):
        try:
            tilename = self.matr[x][y]
        except Exception as e:
            print(e)
            return self.matr[0][0]

        assert tilename != 0, tilename

        return tilename


class ImageFolder:
    def __init__(self, filename):
        self.filename = filename

    def set_tile(self, x, y, zoom):
        pass

    def __call__(self):
        return (np.random.random((256,256,3))*255).astype(np.uint8)
