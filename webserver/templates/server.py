import io
import json
import numpy as np
from pathlib import Path

from PIL import Image
from flask import Flask, make_response, send_file, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    p = Path('imgs')
    imgs = [str(i.name) for i in p.glob('*.tif')]
    href = lambda x: '<a href="http://localhost:9050/' + x + '">'+x+'</a>'
    s = '<br/>'.join([href(i) for i in imgs])
    return s

@app.route("/<string:filename>")
def ll(filename):
    s1 = '''
<!DOCTYPE html>
<head>
 <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"
   integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A=="
   crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"
   integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA=="
   crossorigin=""></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>

<style>
#map {
	width:960px;
	height:1000px;
}
</style>
</head>

<body>
	<div id="map"></div>
<script>
window.onload = function () {
    var map = L.map('map',{crs: L.CRS.Simple});'''

    s2 = '''
    var layer = L.tileLayer('http://localhost:9051/'''

    s3 = '''/{z}_{x}_{y}.png', {
        maxZoom: 10,
        maxNativeZoom: 6,
        maxBounds: [12817, 11172],
    }).addTo(map);
    map.setView([0.0,0.0], 6);

    layer.on('tileload', function(e) {
        console.log(e);
        console.log(e.coords);
        var dd = {'data':"this is a tset"};
        $.ajax({
            type: "POST",
            url: '/test',
            data: JSON.stringify(dd),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){console.log(data);},
            error: function(errMsg) {
                alert(errMsg);
            }
        });

    })
};

'''

    fetch = '''
    '''

    s4 = '''
</script>
</body>
</html>
        '''

    s = s1 +  s2 + filename + s3+s4
    return s 

@app.route('/test', methods=['POST'])
def testfn():    
    data = request.get_json()
    #data = request.form['data']
    print(data, type(data))
    return jsonify({'thisis ':'answer'})  


if __name__ == "__main__":
    app.run(port=9050)


