import io
import json
import urllib
import random
import argparse
from pathlib import Path

from flask import Flask, make_response, send_file, jsonify, request, render_template

app = Flask(__name__)


def log(m): print(m)

@app.route('/')
def index():
    p = Path('/mnt/data').absolute()
    redir = {
            '*.tif': 'view',
            '*.tiff': 'view',
            '*.jpg': 'view',
            '*.jpeg': 'view',
            '*.emb': 'ember/gen',
            'prj.json': 'ember',
            }

    files = []
    for ext in redir:
        files.append(p.rglob(ext)) 

    s = ''
    for fns, ext in zip(files, redir):
        s+=f'<h2>{ext}</h2>'
        for fn in sorted(fns):
            fn_sub_path = str(fn.relative_to(p))
            re_fn_sub_path = urllib.parse.quote(fn_sub_path, safe='')
            url = f'<a href="{redir[ext]}/' + re_fn_sub_path + '">'+fn_sub_path+'</a>'
            s += url
            s += '<br/>\n'

    return s

@app.route("/view/<path:filename>")
def viewer(filename):
    if app.debug: log(f'FILENAME: {filename}')
    return render_template('view_template.html', filename=filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', const=True, default=False, nargs='?', help='debug')
    args = parser.parse_args()
    host, port = '0.0.0.0', 5000
    app.run(host=host, port=port, debug=args.d)



