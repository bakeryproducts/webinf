import argparse
import werkzeug
from werkzeug.routing import PathConverter
from packaging import version
from flask import Flask, jsonify, request
from pathlib import Path

from readers import PamReader, PamWriter

app = Flask(__name__)
# whether or not merge_slashes is available and true
MERGES_SLASHES = version.parse(werkzeug.__version__) >= version.parse("1.0.0")


def log(m): print(m)


class EverythingConverter(PathConverter):
    regex = '.*?'


app.url_map.converters['everything'] = EverythingConverter
config = {"merge_slashes": False} if MERGES_SLASHES else {}


@app.route('/label/<everything:filename>', **config)
def ann_selector(filename):
    if app.debug: log(filename)
    filename = filename.replace('__', '/')
    filename = Path('/mnt/data') / Path(filename)
    reader = PamReader(filename)
    return ann_read(reader)


@app.route('/save/<everything:filename>',methods=["GET", "POST"])
def save(filename):
    if request.method == 'POST':
        data = request.json
        pw = PamWriter(filename)
        pw._create_ann(data)
        return jsonify(data)


def ann_read(reader): return jsonify(reader())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--p', default='5000', help='port')
    parser.add_argument('--h', default='0.0.0.0', help='host')
    parser.add_argument('--d', const=True, default=False, nargs='?', help='debug')
    args = parser.parse_args()
    app.run(host=args.h, port=args.p, debug=args.d)
