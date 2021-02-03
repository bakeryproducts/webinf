import io
#import argparse
from pathlib import Path
from PIL import Image
import base64

import numpy as np
from flask import Flask, make_response, send_file, jsonify

app = Flask(__name__)

@app.route("/infer/<string:filename>")
def infer_processer(filename):
    filename = filename.replace('__', '/')
    mask = (np.random.random((200,200,3))*255.).astype(np.uint8)

    img_bytes = io.BytesIO()
    im = Image.fromarray(mask)
    im.convert('RGBA').save(img_bytes, format='PNG')
    img_bytes.seek(0, 0)
    b64_img = base64.b64encode(img_bytes.read())

    #return send_file(img_bytes, mimetype='image/png', as_attachment=False)
    return jsonify({'mask':b64_img.decode('utf-8')})

#@app.route("/proxy-example")
#def proxy_example():
#    r = requests.get("http://example.com/other-endpoint")
#    return Response(
#        r.text
#        status=r.status_code,
#        content_type=r.headers['content-type'],
#    )


if __name__ == "__main__":
    #parser = argparse.ArgumentParser()
    #parser.add_argument('--p', default='7053', help='port')
    #parser.add_argument('--h', default='0.0.0.0', help='host')
    #args = parser.parse_args()
    #app.run(host=args.h, port=args.p)
    app.run()
