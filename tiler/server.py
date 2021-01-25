import io
from PIL import Image
from pathlib import Path

import numpy as np
from flask import Flask, make_response, send_file

from readers import ImageFolder, BigImage

app = Flask(__name__)


@app.route("/<string:filename>/<int:zoom>_<int:x>_<int:y>.png")
def tile_selector(filename, x, y, zoom):
    filename = Path(filename)
    if filename.is_dir(): reader = ImageFolder(filename)
    else: reader = BigImage(filename)

    reader.set_tile(x,y,zoom)
    return tile_reader(reader)
    
def tile_reader(reader):
    # fetch tile
    data = reader() 
    #print(reader.filename, data.shape, data.dtype)
    img_bytes = io.BytesIO()
    im = Image.fromarray(data)
    im.convert('RGBA').save(img_bytes, format='PNG')
    img_bytes.seek(0, 0)

    return send_file(img_bytes, mimetype='image/png', as_attachment=False)

if __name__ == "__main__":
    app.run(port=9051)


