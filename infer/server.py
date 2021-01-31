import io
import requests
import argparse
from pathlib import Path

from flask import Flask, make_response, send_file, jsonify

app = Flask(__name__)

@app.route("/infer/<string:filename>")
def infer_processer(filename):
    filename = filename.replace('__', '/')

# assume that "app" below is your flask app, and that
# "Response" is imported from flask.

@app.route("/proxy-example")
def proxy_example():
    r = requests.get("http://example.com/other-endpoint")
    return Response(
        r.text
        status=r.status_code,
        content_type=r.headers['content-type'],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--p', default='7053', help='port')
    parser.add_argument('--h', default='0.0.0.0', help='host')
    args = parser.parse_args()
    app.run(host=args.h, port=args.p)
