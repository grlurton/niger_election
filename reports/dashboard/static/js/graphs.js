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
			var long , lat , i , locality , popup;
			// Creating clustering markers
			var markers = L.markerClusterGroup({
				maxClusterRadius: 20 ,
				chunkedLoading: true ,
				iconCreateFunction: function(cluster) {
					var children = cluster.getAllChildMarkers();
        	var sum = 0;
					for (var i = 0; i < children.length; i++) {
						sum += children[i].n_population;
					}

    		var c = ' marker-cluster-';
    		if (sum < 50000) {
        		c += 'small';
    		} else if (sum < 100000) {
        		c += 'medium';
    		} else if (sum < 500000){
        		c += 'large';
    		} else if (sum < 1000000){
        		c += 'semi-large';
    		} else{
      			c += 'very-large';
    		}
				return new L.DivIcon({ html: '<div><span><b>' + sum + '</b></span></div>',
															className: 'marker-cluster' + c,
															iconSize:  L.point(40, 40) });
    }
    });

			for (i = 0 ; i < records.length ; i++) {
				long = records[i]['longitude'] ;
				lat = records[i]['latitude'] ;
				locality = records[i].locality
				n_population = records[i].n_population

				popup =  '<b> Locality : </b>'+ records[i].locality +
									'<br/><b> Population : </b>' + records[i].n_population ;

				local_marker = L.circleMarker([lat,long] , {title: locality , n_population: n_population}).bindPopup(popup).openPopup() ;
				local_marker.n_population = records[i].n_population ;
				markers.addLayer(local_marker) ;
			}
			map.addLayer(markers);

			// Adding search box
			var controlSearch = new L.Control.Search({
					position:'topright',
					layer: markers,
					initial: false,
					zoom: 12,
					marker: false
				});

				map.addControl( controlSearch );
  };
	drawMap();
};
