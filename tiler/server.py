import io
import argparse
from PIL import Image
from pathlib import Path

import numpy as np
from flask import Flask, make_response, send_file, send_from_directory, Response

from readers import ImageFolder, BigImage, JsonReader

app = Flask(__name__)
readers = {}

def log(m): print(m)

def create_reader(filename):
    global readers

    filename = filename.replace('__', '/')
    prefix = Path('/mnt/data')
    filename =  prefix / Path(filename)

    if filename in readers: return readers[filename]

    if filename.exists(): 
        if filename.is_dir(): reader = ImageFolder(filename)
        elif filename.suffix == '.tiff' or filename.suffix == '.tif': reader = BigImage(filename)
        elif filename.suffix == '.json': 
            reader = JsonReader(filename, prefix='')
            readers[filename] = reader
    else:
        log(f'filename is not valid: {filename}')
        return None

    return reader

@app.route("/tile/embtile/<string:filename>/<int:zoom>_<int:x>_<int:y>")
def emb_selector(filename, zoom, x, y):
    if app.debug: log(f'emb q {filename}, {x}, {y}, {zoom}')
    reader = create_reader(filename)
    img_name = reader.get_img_from_xyz(x,y,zoom)
    if app.debug: log(f'EMBTILE {img_name}')
    #return send_file(img_name, mimetype='image/png', as_attachment=False)
    return Response(mimetype='image/png', headers=[('X-Accel-Redirect', f'/storage/{img_name}')])


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
    parser.add_argument('--d', const=True, default=False, nargs='?', help='debug')
    args = parser.parse_args()
    host, port = '0.0.0.0', 5000
    app.run(host=host, port=port, debug=args.d)


