import io
from pathlib import Path
import numpy as np

from PIL import Image
from flask import Flask, make_response, send_file

app = Flask(__name__)

from readers import ImageFolder, BigImage



@app.route("/<string:filename>/<int:zoom>_<int:x>_<int:y>.png")
def tile_selector(filename, x, y, zoom):
    filename = Path(filename)
    if filename.is_dir():
        reader = ImageFolder(filename)
    else:
        reader = BigImage(filename)

    reader.set_tile(x,y,zoom)
    return tile_reader(reader)
    


def tile_reader(reader):
    # fetch tile
    data = reader() 
    print(reader.filename, data.shape, data.dtype)
    # display tile
    bio = io.BytesIO()
    im = Image.fromarray(data)
    im.convert('RGBA').save(bio, format='PNG')
    bio.seek(0, 0)

    return send_file(bio, mimetype='image/png', as_attachment=False)
#    bio = io.BytesIO()
#    im = Image.fromarray(data)
#    im.save(bio, 'PNG')
#    print(bio)
#    return send_file(bio,
#                 attachment_filename='logo.png',
#                 mimetype='image/png')

#    response = make_response(bio.getvalue())
#    response.headers['Content-Type'] = 'image/png'
#    response.headers['Content-Disposition'] = 'filename=%d.png' % 0
#    return response


if __name__ == "__main__":
    uri = "file:///tmp/python-catalog/"
    app.run(port=5051)


