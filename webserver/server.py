import io
import json
import argparse
import numpy as np
from pathlib import Path

from PIL import Image
from flask import Flask, make_response, send_file, jsonify, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    p = Path('/mnt/data').absolute()
    imgs, exts = [], ['*.tif', '*.tiff']
    for ext in exts:
        imgs.extend(p.rglob(ext)) 

    s = ''
    for img in imgs:
        img_sub_path = str(img.relative_to(p))
        re_img_sub_path = img_sub_path.replace('/', '__') # potomuchto.
        url = f'<a href="view/' + re_img_sub_path + '">'+img_sub_path+'</a>'
        s += url
        s += '<br/>\n'
    return s

@app.route("/view/<string:filename>")
def ll(filename):
    print(f'FILENAME: {filename}')
    global TILE_HOST 
    global TILE_PORT
    return render_template('ll_template.html', TILE_HOST=TILE_HOST, TILE_PORT=TILE_PORT, filename=filename)


@app.route('/test')
def testfn():    
    data = request.get_json()
    return jsonify({'thisis ':'answer'})  


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--th', default='localhost', help='tile host')
    parser.add_argument('--tp', default='7088', help='tile port')

    parser.add_argument('--h', default='0.0.0.0', help='web server host')
    parser.add_argument('--p', default='7050', help='web server port')

    args = parser.parse_args()
    TILE_HOST = args.th
    TILE_PORT = args.tp

    app.run(host=args.h, port=args.p)






