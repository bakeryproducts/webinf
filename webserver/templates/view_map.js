var map = L.map('map', {
        crs: L.CRS.Simple,
        center: [0, 0],
        zoom: 5,
    });
var local_url = document.location.origin;
var s = `http:\/\/${local_url}:`;
console.log(s, local_url);
console.log('{{filename}}');

var layer = L.tileLayer(local_url + '/tile/{{filename}}/{z}_{x}_{y}.png', {
    maxZoom: 10,
    maxNativeZoom: 6,
}).addTo(map);

function getBoxTiles(){
    var zoom = map.getZoom()
    var min = map.project(map.getBounds().getNorthWest(), zoom).divideBy(256).floor(),
        max = map.project(map.getBounds().getSouthEast(), zoom).divideBy(256).floor(),
        cds = [],
        mod = Math.pow(2, zoom);

    console.log(min.x, min.y, max.x, max.y)

    var l = Math.max(0, min.x);
    var t = Math.max(0, min.y);
    
    // TODO right and bottom boundaries requieres max tile num, of W,H info... 
    return [l,t,max.x, max.y];
}

function onKeyPressed(e) {
    console.log("Key", e);
    if (e.key === "i") {
        var filename = '{{filename}}';
        var [l,t,r,b] = getBoxTiles();
        var zoom = map.getZoom();
        if (zoom >6){
            return
        }
            
        mod = Math.pow(2, zoom);
        s = 256/mod;
        console.log(l,t,r,b, s, mod)

        L.polyline([[-t*s, l*s], 
                    [-t*s, r*s],
                    [-b*s, r*s],
                    [-b*s, l*s],
                    [-t*s, l*s], 
        ], {color:'red', weight: 1}).addTo(map);

        var url = `/infer/${filename}/${zoom}_${l}_${t}_${r-1}_${b-1}`;
        imageBounds = [[-t*s, l*s], [-b*s, r*s]];
        L.imageOverlay(url, imageBounds, {opacity:1}).addTo(map).bringToFront();

    };
};
document.addEventListener("keypress", onKeyPressed)


L.Draw.Polygon.prototype._onTouch = L.Util.falseFn;
L.drawLocal.draw.handlers.polygon.tooltip.cont = '';
L.drawLocal.draw.handlers.polygon.tooltip.start = '';
L.drawLocal.draw.handlers.polygon.tooltip.end = '';
L.drawLocal.edit.handlers.edit.tooltip.text = ''
L.drawLocal.edit.handlers.edit.tooltip.subtext = ''

var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
    position: 'topright',
    draw: {
        polygon: {
            shapeOptions: {
                color: 'blue',
                weight: 10
            },
            allowIntersection: false,
            drawError: {
                color: 'orange',
                timeout: 100
            },
            showArea: false,
            metric: true,
            repeatMode: true
        },
        polyline : false,
        rectangle : false,
        circle : false,
        circlemarker : false,
        marker: false,
    },
    edit: {
        featureGroup: drawnItems
    }
});
map.addControl(drawControl);

map.on('draw:created', function (e) {
    var type = e.layerType,
        layer = e.layer;
    drawnItems.addLayer(layer);
});

$("#demo_btn").on("click", function() {
        var polys = [];
        var rawp = drawnItems.toGeoJSON()['features'];
        rawp.forEach(function(poly){
            pp = poly['geometry']['coordinates'][0];
            polys.push(pp);
            });
        console.log(polys);

        var js_data = JSON.stringify(polys);
        $.ajax({                        
            url: '/save/{{filename}}',
            type : 'post',
            contentType: 'application/json',
            dataType : 'json',
            data : js_data
        }).done(function(result) {
            //console.log(result);
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.log("fail: ",textStatus, errorThrown);
        });
    });



$.ajax({
    type: "GET",
    url: '/label/{{filename}}',
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function(all_polys){
            console.log('LOADED');
            all_polys.forEach(function(polys){
                polys.forEach(function(e){
                    //new L.Polyline(e, {
                    new L.Polygon(e, {
                        color: 'green',
                        weight: 7,
                        //opacity: .3,
                        //smoothFactor: 1
                    //}) .addTo(map);
                    }) .addTo(drawnItems);
                });
            });
    },
    error: function(errMsg) {
        //alert(errMsg);
    }
});
