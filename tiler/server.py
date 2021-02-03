import io
import os
from PIL import Image
from pathlib import Path

import numpy as np
from flask import Flask, make_response, send_file

from readers import ImageFolder, BigImage

app = Flask(__name__)
app.config.update(TEMPLATES_AUTO_RELOAD=True)

def create_reader(filename):
    filename = filename.replace('__', '/')
    filename = Path(os.getenv('STORAGE')) / Path(filename)
    
    if filename.exists(): 
        if filename.is_dir(): reader = ImageFolder(filename)
        else: reader = BigImage(filename)
    else:
        print(f'filename is not valid: {filename}')
        return None
    return reader

@app.route("/tile/<string:filename>/<int:zoom>_<int:x>_<int:y>.png")
def tile_selector(filename, x, y, zoom):
    reader = create_reader(filename)
    data = reader.read_tile(x,y,zoom)
    return send_image(data)
    
@app.route("/tile/<string:filename>/<int:zoom>_<int:l>_<int:t>_<int:r>_<int:b>")
def raster_selector(filename, zoom, l,t,r,b):
    reader = create_reader(filename)
    data = reader.read_raster(l,t,r,b, zoom)
    data[...,0] *=0
    return send_image(data)

def send_image(data):
    img_bytes = io.BytesIO()
    im = Image.fromarray(data)
    im.convert('RGBA').save(img_bytes, format='PNG')
    img_bytes.seek(0, 0)
    return send_file(img_bytes, mimetype='image/png', as_attachment=False)


if __name__ == "__main__":
    app.run()
