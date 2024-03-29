import io
import json
import urllib
import random
import argparse
import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, request, render_template, abort, redirect, url_for

from projector import generate_projection
import matplotlib.pyplot as plt


app = Flask(__name__)

def log(m): print(m)

@app.route("/ember/gen/<path:filename>", methods=['POST', 'GET'])
def post_em(filename):
    if request.method == 'POST':
        prefix = Path('/mnt/data')
        fn = urllib.parse.unquote(filename)


        N = int(request.form.get('N', 10)) ** 2
        tile_name = request.form.get('tile_name', None)
        selector = 'nearest' if tile_name else 'rand'
        metric = request.form.get('metric', None)
        data_path = request.form.get('data_path', '')

        proj_name = request.form.get('proj_name', None)
        if not proj_name:
            proj_name = f'{N}_' + '{:%b_%d_%H_%M_%S}'.format(datetime.datetime.now())

        path = generate_projection(src=prefix/fn, 
                                    n=N,
                                    tile_size=128, 
                                    data_path=data_path,
                                    proj_name=proj_name,
                                    metric=metric,
                                    selector=selector, 
                                    key_name=tile_name)

        path = path.relative_to(prefix)

        url = url_for('.ember', filename=path, _external=True)
        return redirect(url)
    else:
        def_N = 10
        def_data_path = 'input/splits/cropped_128_0'
        return render_template('embedding_start.html', filename=filename, def_data_path=def_data_path, def_N=def_N)

def generate_grid(emb_data):
    nn = int(emb_data['n']**.5)
    tile_size = emb_data['tile_size']
    scale = 2**6

    gr = np.array(np.meshgrid(-np.linspace(0, 1, nn), np.linspace(0, 1, nn)))

    lt = gr * (nn-1)*tile_size / scale
    rt = np.copy(lt)
    rt[0] -= tile_size / scale

    lb = np.copy(lt)
    lb[1] += tile_size / scale

    rb = np.copy(lt)
    rb[0] -= tile_size / scale
    rb[1] += tile_size / scale

    polys = []
    
    for i in range(nn):
        for j in range(nn):
            p = [lt[:, i, j], lb[:, i, j], rb[:, i, j], rt[:, i, j]]
            p = [t.tolist() for t in p]
            polys.append((i,j,p))

    return polys


def get_js_poly_args(**kwargs):
    d = js_poly_args = dict(
            color= 'tomato',
            opacity=.4,
            weight= 3,
            fillColor= 'red',
            fillOpacity= .0,
        )
    d.update(**kwargs)
    return d

def convert_polys(polys, data, label=None, **kwargs):
    conv_polys = []
    for i,j,p in polys:
        idx = (data['x'] == i) & (data['y'] == j)
        if label is None:
            color = 'tomato'
            message = data.loc[idx]['fn'].values[0]
        else:
            color_float = data.loc[idx][label].values[0]
            color = plt.cm.jet(float(color_float))[:-1]  
            color = [int(c*255) for c in color]
            color = f'rgb{tuple(color)}'
            message = str(color_float)

        js_poly_args = get_js_poly_args(color=color, **kwargs)

        d = {
                'points': p,
                'args': js_poly_args,
                'message': message,
            }
        conv_polys.append(d)
    return conv_polys


@app.route("/ember/<path:filename>")
def ember(filename):
    if app.debug: log(f'FILENAME: {filename}')
    fn = urllib.parse.unquote(filename)

    prefix = Path('/mnt/data')
    labels_pattern = 'labels_*'
    label_fns = list((prefix/fn).parent.parent.glob(labels_pattern))

    with open(str(prefix/fn), 'r') as f:
        emb_data = json.load(f)

    WIDTH, HEIGHT = emb_data['width'], emb_data['height']
    TS = emb_data['tile_size']
    selected_data = pd.read_csv(str((prefix/fn).parent / emb_data['proj']))

    labels_polys = []
    for ln in label_fns:
        n = ln.with_suffix('').name
        l_polys = convert_polys(generate_grid(emb_data), selected_data, label=str(ln.name), opacity=.7)
        labels_polys.append([n, l_polys])

    polys = [
                ['grid', convert_polys(generate_grid(emb_data), selected_data, label=None, opacity=0.)],
                *labels_polys
            ]
    
    return render_template('embedding_template.html', WIDTH=WIDTH, HEIGHT=HEIGHT, polygons_set=polys, filename=filename)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', const=True, default=False, nargs='?', help='debug')
    args = parser.parse_args()
    host, port = '0.0.0.0', 5000
    app.run(host=host, port=port, debug=args.d)


