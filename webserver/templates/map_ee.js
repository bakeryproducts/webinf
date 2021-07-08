let map = L.map('map',{
    crs: L.CRS.Simple,
    maxZoom: 10,
    minZoom: 0,
    maxNativeZoom: 6,
    minNativeZoom: 6,
    zoomSnap: 0.5,
    zoomDelta: 0.5,
    wheelPxPerZoomLevel: 240,
});
map.setView([-30.0,30.0], 6);
let local_url = document.location.origin;
local_url = local_url.split(':').slice(0,-1).join(':');
console.log(local_url, );
let layer = L.tileLayer( local_url + ':{s}/tile/embtile/{{filename}}/{z}_{x}_{y}', {
    maxZoom: 10,
    minZoom: 0,
    maxNativeZoom: 6,
    minNativeZoom: 6,
    tileSize: 128,
    subdomains: ['7034', '7035', '7036', '7037'],
}).addTo(map);

