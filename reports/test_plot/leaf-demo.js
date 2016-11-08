var map = L.map( 'map', {
	center: [20.0, 5.0],
	minZoom: 2,
	zoom: 2
});

var layer = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
  });
  
  // Now add the layer onto the map
  map.addLayer(layer);