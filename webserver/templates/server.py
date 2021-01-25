import io
import numpy as np
from pathlib import Path

from PIL import Image
from flask import Flask, make_response, send_file

app = Flask(__name__)

@app.route('/')
def index():
    s = '''
    hello!

    '''
    return s

@app.route("/<string:filename>")
def ll(filename):
    s1 = '''
    <!DOCTYPE html>
    <head>
    <link rel="stylesheet" href="static/leaflet/leaflet.css" />
    <script src="static/leaflet/leaflet.js"></script>
    <script src="static/jquery-2.2.2.min.js"></script>

    <style>
    #my-map {
            width:1000px;
            height:1000px;
    }
    </style>
    </head>

    <body>
            <div id="map"></div>
    <script>
    '''

    s2 = '''
    window.onload = function () {
        //http://localhost:5000/test/{z}_{x}_{y}.png
        //http://{s}.tile.osm.org/{z}/{x}/{y}.png
        var map = L.map('map',{crs: L.CRS.Simple});
        L.tileLayer('http://localhost:9051/'''


    s3 = '''/{z}_{x}_{y}.png', {
            maxZoom: 10,
            maxNativeZoom: 6,
            maxBounds: [12817, 11172],
        }).addTo(map);
        map.setView([0.0,0.0], 6);
    };
    </script>
    </body>
    </html>
    '''

    s = s1 +'\n'+ s2 + filename + s3  
    return s


if __name__ == "__main__":
    app.run(port=9050)


