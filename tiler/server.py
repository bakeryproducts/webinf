import io
from PIL import Image
from pathlib import Path

import numpy as np
from flask import Flask, make_response, send_file

from readers import ImageFolder, BigImage

app = Flask(__name__)


@app.route("/tile/<string:filename>/<int:zoom>_<int:x>_<int:y>.png")
def tile_selector(filename, x, y, zoom):
    filename = filename.replace('__', '/')
    filename = Path('/mnt/data') / Path(filename)
    print(filename)
    
    if filename.exists(): 
        if filename.is_dir(): reader = ImageFolder(filename)
        else: reader = BigImage(filename)
    else:
        print(f'filename is not valid: {filename}')
        return None

    return tile_read(reader,x,y,zoom)
    
def tile_read(reader,x,y,zoom):
    # fetch tile
    data = reader(x,y,zoom)

    #print(reader.filename, data.shape, data.dtype)
    img_bytes = io.BytesIO()
    im = Image.fromarray(data)
    im.convert('RGBA').save(img_bytes, format='PNG')
    img_bytes.seek(0, 0)

    return send_file(img_bytes, mimetype='image/png', as_attachment=False)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7051)
    #app.run(port=7051)
