import io
import json
import argparse
from pathlib import Path

from flask import Flask, make_response, send_file, jsonify, request, render_template

app = Flask(__name__)


def log(m): print(m)

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

    files, exts = [], ['*_emb.csv']
    for ext in exts:
        files.extend(p.rglob(ext)) 

    for ff in files:
        img_sub_path = str(ff.relative_to(p))
        re_img_sub_path = img_sub_path.replace('/', '__') # potomuchto.
        url = f'<a href="emb/' + re_img_sub_path + '">'+img_sub_path+'</a>'
        s += url
        s += '<br/>\n'
    return s

@app.route("/view/<string:filename>")
def viewer(filename):
    if app.debug: log(f'FILENAME: {filename}')
    global TILE_HOST, TILE_PORT
    return render_template('ll_template.html', TILE_HOST=TILE_HOST, TILE_PORT=TILE_PORT, filename=filename)

@app.route("/emb/<string:filename>")
def ember(filename):
    if app.debug: log(f'FILENAME: {filename}')
    global TILE_HOST, TILE_PORT
    return render_template('ee_template.html', TILE_HOST=TILE_HOST, TILE_PORT=TILE_PORT, filename=filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', const=True, default=False, nargs='?', help='debug')
    args = parser.parse_args()
    TILE_HOST, TILE_PORT = 'localhost', 5000
    host, port = '0.0.0.0', 5000
    app.run(host=host, port=port, debug=args.d)






