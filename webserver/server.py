import urllib
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
        '*.svs': 'view',
        '*.jpg': 'view',
        '*.jpeg': 'view',
        '*.png': 'view',
        '*.emb': 'ember/gen',
        'prj.json': 'ember',
    }

    files = []
    s = ''
    for ext in redir:
        all_files = list(p.rglob(ext))
        folders = set()
        for file in all_files:
            folders.add(str(file.parent))

        for folder in list(folders):
            folder = Path(folder)
            folder_files = list(folder.glob(ext))

            prpath = str(folder.relative_to(p))
            s += f'<h2>{prpath}:{ext}</h2>'
            s += '<details>'

            for fn in sorted(folder_files):
                fn_sub_path = str(fn.relative_to(p))
                re_fn_sub_path = urllib.parse.quote(fn_sub_path, safe='')
                url = f'<a href="{redir[ext]}/' + re_fn_sub_path + '">'+fn_sub_path+'</a>'
                s += url
                s += '<br/>\n'
            s+='</details>'

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
