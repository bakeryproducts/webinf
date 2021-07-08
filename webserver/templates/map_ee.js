var map = L.map('map',{
    crs: L.CRS.Simple,
    maxZoom: 10,
    minZoom: 0,
    maxNativeZoom: 6,
    minNativeZoom: 6,
});
map.setView([-30.0,30.0], 6);
var local_url = document.location.origin;
var layer = L.tileLayer(local_url + '/tile/embtile/{{filename}}/{z}_{x}_{y}', {
    maxZoom: 10,
    minZoom: 0,
    maxNativeZoom: 6,
    minNativeZoom: 6,
    tileSize: 128,
}).addTo(map);

