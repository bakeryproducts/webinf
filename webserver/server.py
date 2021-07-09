import io
import json
import random
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

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

    files, exts = [], ['emb.json']
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
    return render_template('view_template.html', filename=filename)

@app.route("/emb/<string:filename>")
def ember(filename):
    if app.debug: log(f'FILENAME: {filename}')

    fn = filename.replace('__', '/')
    prefix = Path('/mnt/data')
    with open(str(prefix/fn), 'r') as f:
        data = json.load(f)

    WIDTH, HEIGHT = data['width'], data['height']
    TS = data['tile_size']
    df = pd.read_csv(str((prefix/fn).parent / data['proj']))


    nn = int(data['n']**.5)
    ts = data['tile_size']
    sc = 2**6
    gr = np.array(np.meshgrid(-np.linspace(0, 1, nn), np.linspace(0, 1, nn)))

    lt = gr * (nn-1)*ts / sc
    rt = np.copy(lt)
    rt[0] -= ts/sc

    lb = np.copy(lt)
    lb[1] += ts/sc

    rb = np.copy(lt)
    rb[0] -= ts/sc
    rb[1] += ts/sc

    polys = []
    
    for i in range(nn):
        for j in range(nn):
            p = [lt[:, i, j], lb[:, i, j], rb[:, i, j], rt[:, i, j]]
            p = [t.tolist() for t in p]
            js_poly_args = dict(
                color= 'tomato',
                opacity=.4,
                weight= 3,
                fillColor= 'red',
                fillOpacity= .0,
            )
            js_poly_args['color'] = random.choice(['blue', 'tomato', 'green'])
            message = df.loc[(df['x'] == i) & (df['y'] == j)]['fn'].values[0]
            d = {
                    'points': p,
                    'args': js_poly_args,
                    'message': message,

                }
            polys.append(d)

        
    return render_template('embedding_template.html', WIDTH=WIDTH, HEIGHT=HEIGHT, polys=polys, filename=filename)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', const=True, default=False, nargs='?', help='debug')
    args = parser.parse_args()
    host, port = '0.0.0.0', 5000
    app.run(host=host, port=port, debug=args.d)






