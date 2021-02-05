import io
import argparse
import requests
from pathlib import Path
from PIL import Image

import numpy as np
from flask import Flask, send_file

from mwrap import Inferencer

app = Flask(__name__)

def log(m):print(m)

@app.route("/infer/<string:filename>/<int:zoom>_<int:l>_<int:t>_<int:r>_<int:b>")
def infer_processer(filename, zoom, l, t, r, b):
    global inf, TILE_HOST, TILE_PORT
    r = requests.get(f"http://{TILE_HOST}:{TILE_PORT}/tile/{filename}/{zoom}_{l}_{t}_{r}_{b}")
    img_stream = io.BytesIO(r.content)
    img = np.array(Image.open(img_stream))
    if app.debug : log(f'INF on img: {img.shape}, {img.dtype}')
    img = inf.inference(img)
    if app.debug : log(f'MASK: {img.shape}, {img.dtype}, {img.max()}')
    return send_image(img)

def send_image(data):
    img_bytes = io.BytesIO()
    im = Image.fromarray(data)
    im.convert('RGBA').save(img_bytes, format='PNG')
    img_bytes.seek(0, 0)
    return send_file(img_bytes, mimetype='image/png', as_attachment=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--p', default='7053', help='port')
    parser.add_argument('--h', default='0.0.0.0', help='host')
    parser.add_argument('--tp', default='7051', help='tiler port')

    parser.add_argument('--g', default='0', help='#gpu 1 2 1,2')
    parser.add_argument('--t', default=.5, help='threshold')
    parser.add_argument('--d', const=True, default=False, nargs='?', help='debug')
    
    args = parser.parse_args()
    TILE_PORT = args.tp 
    TILE_HOST = 'tiler' # tiler host is local network, const
    inf = Inferencer(gpus=args.g, threshold=args.t)
    
    app.run(host=args.h, port=args.p, debug=args.d)
