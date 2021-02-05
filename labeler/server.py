import io
import argparse
from pathlib import Path

from flask import Flask, make_response, send_file, jsonify

from readers import PamReader

app = Flask(__name__)


def log(m):print(m)

@app.route("/label/<string:filename>")
def ann_selector(filename):
    if app.debug: log(filename)
    filename = filename.replace('__', '/')
    filename = Path('/mnt/data') / Path(filename)
    reader = PamReader(filename)
    return ann_read(reader)
    
def ann_read(reader): return jsonify(reader())  

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--p', default='7052', help='port')
    parser.add_argument('--h', default='0.0.0.0', help='host')
    parser.add_argument('--d', const=True, default=False, nargs='?', help='debug')
    args = parser.parse_args()
    app.run(host=args.h, port=args.p, debug=args.d)
