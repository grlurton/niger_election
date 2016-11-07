queue()
	.defer(d3.json,"/data")
	.await(makeGraphs);

function makeGraphs(error, recordsJson){

	var records = recordsJson

  records.forEach(function(d) {
    d["longitude"] = +d["longitude"];
    d["latitude"] = +d["latitude"];

  });

	var map = L.map('map');

	var drawMap = function(){
  	// {s}, {z}, {x} and {y} are placeholders for map tiles
  	// {x} and {y} are the x/y of where you are on the map
  	// {z} is the zoom level
  	// {s} is the subdomain of cartodb
      map.setView([17.6078, 8.0817], 5);
      L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
  }).addTo(map);
  	// Now add the layer onto the map
  	  
	    //L.marker(d['latitude'][1],d['longitude'][1]).addTo(map).bindPopup("<strong>d['location'][1]</strong>").openPopup();
  };
  drawMap();
};