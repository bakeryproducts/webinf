from pathlib import Path

import gdal
import numpy as np

class _Image:
    def __init__(self, filename, info=None):
        self.filename = Path(filename)
        self.info = info
        self._base_zoom_level = 6
        self._base_tile_side = 256

    def convert_tile_idx(x,y,z):
        # returns (x0,x1),(y0,y1) px coordinates of that tile
        p = z-self._base_zoom_level-1
        crop_side = self._base_tile_side * 2**p
        crop_reg = ((x-1)*crop_side, (y-1)*crop_side),(crop_side, crop_side)
        return crop_reg

    def read_part(self):
        raise NotImplementedError


class BigImage(_Image):

    def set_tile(self, x, y, zoom):
       #dims = [file.RasterXSize, file.RasterYSize]
       self.x, self.y, self.z = x,y,zoom
       self.file = gdal.Open(str(self.filename), gdal.GA_ReadOnly)

    def __call__(self):
        return self.read_part()

    def read_part(self):
        # called (in mp) after set_tile
        x,y,w,h = self.convert_tile_idx(self.x, self.y, self.z)
        block = self.file.ReadAsArray(xoff=x, yoff=y, xsize=w, ysize=h)
        return block



class ImageFolder:
    def __init__(self, filename):
        self.filename = filename

    def set_tile(self, x, y, zoom):
        pass

    def __call__(self):
        return (np.random.random((256,256,3))*255).astype(np.uint8)
