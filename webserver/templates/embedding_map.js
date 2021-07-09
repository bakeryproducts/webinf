const DEF_ZOOM = 6;
let h = -{{HEIGHT}}/Math.pow(2,DEF_ZOOM);
let w = {{WIDTH}}/Math.pow(2,DEF_ZOOM);
var bounds = [[0,0], [h, w]];

let local_url = document.location.origin;
local_url = local_url.split(':').slice(0,-1).join(':');
console.log(local_url, );
let baselayer = L.tileLayer( local_url + ':{s}/tile/embtile/{{filename}}/{z}_{x}_{y}', {
    maxZoom: 10,
    minZoom: 0,
    maxNativeZoom: 6,
    minNativeZoom: 6,
    tileSize: 128,
    subdomains: ['7034', '7035', '7036', '7037'],
    bounds: bounds,
});

let map = L.map('map',{
    crs: L.CRS.Simple,
    maxZoom: 10,
    minZoom: 0,
    maxNativeZoom: 6,
    minNativeZoom: 6,
    zoomSnap: 0.5,
    zoomDelta: 0.5,
    wheelPxPerZoomLevel: 240,
    layers: [baselayer],
});

map.setView([h/2.0, w/2.0], DEF_ZOOM);

function poly_click(name){
    alert(name);
    //console.log(name);
}
polyGroup = new L.FeatureGroup();

for(let poly_obj of {{polys}}){
    let poly = poly_obj['points'];
    let name = poly_obj['message'];
    let poly_args = poly_obj['args'];
    //console.log(poly_args);

    let d = 128/5/256;
    poly = [
                [   
                    poly[0][0] -d,
                    poly[0][1] +d 
                ],
                [   
                    poly[1][0] -d ,
                    poly[1][1] -d 
                ],
                [   
                    poly[2][0] +d ,
                    poly[2][1] -d 
                ],
                [   
                    poly[3][0] +d,
                    poly[3][1] +d
                ],
    ];
    let p =  L.polygon(poly, poly_args).bindPopup(name);
    polyGroup.addLayer(p);
    //p.on('click', function(){poly_click(name)});
}

let polyMaps = { 'grid': polyGroup }

L.control.layers(null, polyMaps).addTo(map);


