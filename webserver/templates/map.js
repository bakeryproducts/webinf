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

$.ajax({
    type: "GET",
    url: '/label/{{filename}}',
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function(all_polys){
            var colors = ['red','green','blue'];
            var count = 0;
            all_polys.forEach(function(polys){
                var color = colors[count]
                polys.forEach(function(e){
                    new L.Polyline(e, {
                        color: color,
                        weight: 3,
                        opacity: 1,
                        smoothFactor: 1
                    }) .addTo(map);
                });
                count +=1;
            });
    },
    error: function(errMsg) {
        //alert(errMsg);
    }
});

document.addEventListener("keypress", onKeyPressed)
