import io
import os
import json
from pathlib import Path

from flask import Flask, make_response, send_file, jsonify, request, render_template

app = Flask(__name__)
app.config.update(TEMPLATES_AUTO_RELOAD=True)

@app.route('/')
def index():
    p = Path(os.getenv('STORAGE')).absolute()
    imgs, exts = [], ['*.tif', '*.tiff']
    for ext in exts:
        imgs.extend(p.rglob(ext)) 

    s = ''
    for img in imgs:
        img_sub_path = str(img.relative_to(p))
        re_img_sub_path = img_sub_path.replace('/', '__') # potomuchto.
        url = f'<a href="view/' + re_img_sub_path + '">'+img_sub_path+'</a>'
        s += url
        s += '<br/>'
    return s

@app.route("/view/<string:filename>")
def ll(filename):
    print(f'FILENAME: {filename}')
    TILE_PORT = os.environ['NGX_PORT']
    TILE_HOST = os.environ['NGX_HOST']
    return render_template('ll_template.html', TILE_HOST=TILE_HOST, TILE_PORT=TILE_PORT, filename=filename)

@app.route('/test')
def testfn():    
    data = request.get_json()
    return jsonify({'thisis ':'answer'})  


if __name__ == "__main__":
    TILE_PORT = os.environ['NGX_PORT']
    TILE_HOST = os.environ['NGX_HOST']
    app.run()
