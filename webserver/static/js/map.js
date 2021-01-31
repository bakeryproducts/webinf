

function winload() {
	var map = L.map('full-size',{crs: L.CRS.Simple});
	var layer = L.tileLayer('http://{{TILE_HOST}}:{{TILE_PORT}}/tile/{{filename}}/{z}_{x}_{y}.png', {
		maxZoom: 10,
		maxNativeZoom: 6,
		maxBounds: [12817, 11172],
	}).addTo(map);

	map.setView([0.0,0.0], 6);
	$.ajax({
		type: "GET",
		url: '/label/{{filename}}',
		//data: JSON.stringify(dd),
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function(data){
			//console.log(data);
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
};
