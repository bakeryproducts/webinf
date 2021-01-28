import io
import json
import numpy as np
from pathlib import Path

from PIL import Image
from flask import Flask, make_response, send_file, jsonify, request, render_template

app = Flask(__name__)
WEB_HOST, WEB_PORT = 'localhost', '9050'
TILE_HOST, TILE_PORT = 'localhost', '9051'

@app.route('/')
def index():
    p = Path('../imgs').absolute()
    imgs, exts = [], ['*.tif', '*.tiff']
    for ext in exts:
        imgs.extend(p.rglob(ext)) 

    s = ''
    for img in imgs:
        img_sub_path = str(img.relative_to(p))
        img_sub_path = img_sub_path.replace('/', '__')
        url = f'<a href="http://{WEB_HOST}:{WEB_PORT}/' + img_sub_path + '">'+img_sub_path+'</a>'
        s += url
        s += '<br/>'

    return s

@app.route("/<string:filename>")
def ll(filename):
    print(f'FILENAME: {filename}')
    return render_template('ll_template.html', TILE_HOST=TILE_HOST, TILE_PORT=TILE_PORT, filename=filename)

@app.route('/test', methods=['POST'])
def testfn():    
    data = request.get_json()
    #data = request.form['data']
    #print(data, type(data))
    return jsonify({'thisis ':'answer'})  


if __name__ == "__main__":
    app.run(port=WEB_PORT)


