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
    imgs_list, imgs, exts = [], [], ['*.tif', '*.tiff']
    [imgs.extend(p.rglob(ext)) for ext in exts]
    for img in imgs:
        img_sub_path = str(img.relative_to(p))
        imgs_list.append({
            'ref': img_sub_path.replace('/', '__'), 
            'name': img_sub_path
        })
    return render_template('route.html', imgs=imgs_list)

@app.route("/view/<string:filename>")
def ll(filename):
    print(f'FILENAME: {filename}')
    return render_template('route.html',
		TILE_HOST=os.environ['NGX_HOST'], 
		TILE_PORT=os.environ['NGX_PORT'],
		filename=filename)

@app.route('/test')
def testfn():    
    data = request.get_json()
    return jsonify({'thisis ':'answer'})  


if __name__ == "__main__":
    TILE_PORT = os.environ['NGX_PORT']
    TILE_HOST = os.environ['NGX_HOST']
    app.run()
