import io
import argparse
import requests
from pathlib import Path
from PIL import Image

import numpy as np
from flask import Flask, send_file

from mwrap import Inferencer

app = Flask(__name__)


@app.route("/infer/<string:filename>/<int:zoom>_<int:l>_<int:t>_<int:r>_<int:b>")
def infer_processer(filename, zoom, l, t, r, b):
    global inf, TILE_HOST, TILE_PORT
    r = requests.get(f"http://{TILE_HOST}:{TILE_PORT}/tile/{filename}/{zoom}_{l}_{t}_{r}_{b}")
    img_stream = io.BytesIO(r.content)
    img = np.array(Image.open(img_stream))
    
    img = inf.inference(img)
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
    parser.add_argument('--g', default='0', help='#gpu 1 2 1,2')
    parser.add_argument('--tp', default='7051', help='tiler port')
    
    args = parser.parse_args()
    TILE_PORT = args.tp 
    TILE_HOST = 'tiler' # tiler host is local network, const
    inf = Inferencer(gpus=args.g)
    
    app.run(host=args.h, port=args.p)
