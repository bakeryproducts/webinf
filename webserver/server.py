import io
import json
import numpy as np
from pathlib import Path

from PIL import Image
from flask import Flask, make_response, send_file, jsonify, request, render_template

app = Flask(__name__)

NGINX_HOST, NGINX_PORT = 'localhost', '8887'
WEB_HOST, WEB_PORT = 'webserver', '7050'
TILE_HOST, TILE_PORT = 'tiler', '7051'
LOCALHOST = '0.0.0.0'

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
        url = f'<a href="http://{NGINX_HOST}:{NGINX_PORT}/view/' + re_img_sub_path + '">'+img_sub_path+'</a>'
        s += url
        s += '<br/>'
    return s

@app.route("/view/<string:filename>")
def ll(filename):
    #print(f'FILENAME: {filename}')
    #_, filename = filename.split('/', 1)
    print(f'FILENAME: {filename}')
    #return render_template('ll_template.html', TILE_HOST=TILE_HOST, TILE_PORT=TILE_PORT, filename=filename)
    return render_template('ll_template.html', TILE_HOST=NGINX_HOST, TILE_PORT=NGINX_PORT, filename=filename)

@app.route('/test')
def testfn():    
    data = request.get_json()
    #data = request.form['data']
    #print(data, type(data))
    return jsonify({'thisis ':'answer'})  


if __name__ == "__main__":
    app.run(host=LOCALHOST, port=WEB_PORT)
