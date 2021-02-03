import io
import argparse
import requests
from pathlib import Path
from PIL import Image

from mwrap import inference

import numpy as np
from flask import Flask, make_response, send_file, jsonify

app = Flask(__name__)

@app.route("/infer/<string:filename>/<int:zoom>_<int:l>_<int:t>_<int:r>_<int:b>")
def infer_processer(filename, zoom, l, t, r, b):
    TILE_HOST, TILE_PORT = 'tiler', "7051"
    r = requests.get(f"http://{TILE_HOST}:{TILE_PORT}/tile/{filename}/{zoom}_{l}_{t}_{r}_{b}")
    img_stream = io.BytesIO(r.content)
    img = np.array(Image.open(img_stream))
    print(img.shape)
    res = inference(img)
    return send_image(res)

def send_image(data):
    img_bytes = io.BytesIO()
    im = Image.fromarray(data)
    im.convert('RGBA').save(img_bytes, format='PNG')
    img_bytes.seek(0, 0)
    return send_file(img_bytes, mimetype='image/png', as_attachment=False)

#@app.route("/proxy-example")
#def proxy_example():
#    r = requests.get("http://example.com/other-endpoint")
#    return Response(
#        r.text
#        status=r.status_code,
#        content_type=r.headers['content-type'],
#    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--p', default='7053', help='port')
    parser.add_argument('--h', default='0.0.0.0', help='host')
    args = parser.parse_args()
    app.run(host=args.h, port=args.p)
