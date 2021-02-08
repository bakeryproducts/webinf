import io
import argparse
from PIL import Image
from pathlib import Path

import numpy as np
from flask import Flask, make_response, send_file

from readers import ImageFolder, BigImage

app = Flask(__name__)

def log(m): print(m)

def create_reader(filename):
    filename = filename.replace('__', '/')
    filename = Path('/mnt/data') / Path(filename)
    if filename.exists(): 
        if filename.is_dir(): reader = ImageFolder(filename)
        else: reader = BigImage(filename)
    else:
        print(f'filename is not valid: {filename}')
        return None
    return reader

@app.route("/tile/<string:filename>/<int:zoom>_<int:x>_<int:y>.png")
def tile_selector(filename, x, y, zoom):
    if app.debug: log(f'{filename}, {x}, {y}, {zoom}')
    reader = create_reader(filename)
    data = reader.read_tile(x,y,zoom)
    if app.debug: log(f'Returning raster: {data.shape}, {data.dtype}, {data.max()}')
    return send_image(data)
    
@app.route("/tile/<string:filename>/<int:zoom>_<int:l>_<int:t>_<int:r>_<int:b>")
def raster_selector(filename, zoom, l,t,r,b):
    if app.debug: log(f'{filename}, {l}, {t}, {r}, {b}, {zoom}')
    reader = create_reader(filename)
    data = reader.read_image_part(l,t,r,b, zoom)
    if app.debug: log(f'Returning raster: {data.shape}, {data.dtype}, {data.max()}')
    return send_image(data)

def send_image(data):
    img_bytes = io.BytesIO()
    im = Image.fromarray(data)
    im.convert('RGB').save(img_bytes, format='PNG')
    img_bytes.seek(0, 0)
    return send_file(img_bytes, mimetype='image/png', as_attachment=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--p', default='7051', help='port')
    parser.add_argument('--h', default='0.0.0.0', help='host')
    parser.add_argument('--d', const=True, default=False, nargs='?', help='debug')
    args = parser.parse_args()
    app.run(host=args.h, port=args.p, debug=args.d)


