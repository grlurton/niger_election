queue()
	.defer(d3.json,"/data")
	.await(makeGraphs);

function makeGraphs(error, recordsJson){
	var records = recordsJson ;

	// Add Map
	var map = L.map('map');

	var drawMap = function(d){
      map.setView([17.6078, 8.0817], 5);
			mapLink = "<a href='http://openstreetmap.org'>OpenStreetMap</a>";
			// OSM Background
			L.tileLayer(
				'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
					attribution: '&copy; ' + mapLink + ' Contributors', maxZoom: 15,
				}).addTo(map);
			// Adding locations markers
			var long , lat , i , locality ;
			for (i = 0 ; i < records.length ; i++) {
				long = records[i]['longitude'] ;
				lat = records[i]['latitude'] ;
				locality = records[i]['locality']
				console.log(locality)
				L.circleMarker([lat,long]).addTo(map).bindPopup(locality).openPopup() ;
			}
  };
	drawMap();
};
