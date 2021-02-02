var map = L.map('map',{crs: L.CRS.Simple});
map.setView([-30.0,30.0], 6);
console.log('SANITY')
var layer = L.tileLayer('http://{{TILE_HOST}}:{{TILE_PORT}}/tile/{{filename}}/{z}_{x}_{y}.png', {
    maxZoom: 10,
    maxNativeZoom: 6,
}).addTo(map);

function getBoxTiles(){
    var zoom = map.getZoom()
    var min = map.project(map.getBounds().getNorthWest(), zoom).divideBy(256).floor(),
        max = map.project(map.getBounds().getSouthEast(), zoom).divideBy(256).floor(),
        cds = [],
        mod = Math.pow(2, zoom);

    var i = Math.max(0, min.x);
    var j = Math.max(0, min.y);
    var x = (i % mod + mod) % mod;
    var y = (j % mod + mod) % mod;
    var coords = new L.Point(x, y);
    coords.z = zoom;
    cds.push([x,y]);

    var x = (max.x % mod + mod) % mod;
    var y = (max.y % mod + mod) % mod;
    var coords = new L.Point(x, y);
    coords.z = zoom;
    cds.push([x,y]);
    return cds;
}

function onKeyPressed(e) {
    console.log("Key", e);
    if (e.key === "i") {
        var filename = '{{filename}}';
        var cds = getBoxTiles();
        var zoom = map.getZoom();
        mod = Math.pow(2, zoom);
        var [r,b] = cds[1]
        var [l,t] = cds[0]
        r+=1;
        b+=1;

        var url = `/tile/${filename}/${zoom}_${cds[0][0]}_${cds[0][1]}_${cds[1][0]}_${cds[1][1]}`;
        imageBounds = [[-256*t/mod, l*256/mod], [-b*256/mod, r*256/mod]];
        L.imageOverlay(url, imageBounds, {opacity:.3}).addTo(map).bringToFront();

        L.polyline([[-t*256/mod, l*256/mod], 
                    [-t*256/mod, r*256/mod],
                    [-b*256/mod, r*256/mod],
                    [-b*256/mod, l*256/mod],
                    [-t*256/mod, l*256/mod], 
        ], {color:'red', weight: 2}).addTo(map);
    };
};



$.ajax({
    type: "GET",
    url: '/label/{{filename}}',
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function(data){
            data.forEach(function(e){
                new L.Polyline(e, {
                    color: 'red',
                    weight: 3,
                    opacity: 1,
                    smoothFactor: 1
                }) .addTo(map);
            });

        },
    error: function(errMsg) {
        //alert(errMsg);
    }
});

document.addEventListener("keypress", onKeyPressed)
