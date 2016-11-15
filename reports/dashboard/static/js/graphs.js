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
			var markers = L.markerClusterGroup({
				iconCreateFunction: function(cluster) {
        return L.divIcon({ html: '<b>' +  + '</b>' });
    }
    });
			// OSM Background
			L.tileLayer(
				'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
					attribution: '&copy; ' + mapLink + ' Contributors', maxZoom: 15,
				}).addTo(map);

			var markersLayer = new L.LayerGroup();
			// Adding locations markers
			var long , lat , i , locality , popup;
			// Creating clustering markers
			var markers = L.markerClusterGroup({
				iconCreateFunction: function(cluster) {
					var childCount = cluster.getChildCount();
					var children = cluster.getAllChildMarkers();
        	var sum = 0;
					for (var i = 0; i < children.length; i++) {
						sum += children[i].population;
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
    }
      else{
      	c += 'very-large';
      }
    return new L.DivIcon({ html: '<div><span><b>' + sum+ '</b></span></div>', className: 'marker-cluster' + c, iconSize: new L.Point(40, 40) });
    }
    });
			/*{
				maxClusterRadius: 20 ,
				chunkedLoading: true ,
				iconCreateFunction: function(cluster) {
					var children = cluster.getAllChildMarkers();
        	var sum = 0;
					for (var i = 0; i < children.length; i++) {
						sum += children[i].n_population;
					}
				return new L.DivIcon({html: sum, className : 'marker-cluster', iconSize: L.point(10,10)});
    }
	});

			for (i = 0 ; i < records.length ; i++) {
				long = records[i]['longitude'] ;
				lat = records[i]['latitude'] ;
				locality = records[i].locality

				popup =  '<b> Locality : </b>'+ records[i].locality +
									'<br/><b> Population : </b>' + records[i].n_population ;

				local_marker = L.circleMarker([lat,long] , {title: locality}).bindPopup(popup).openPopup() ;
				local_marker.n_population = records[i].n_population ;
				markers.addLayer(local_marker) ;
			}
			map.addLayer(markers);

			var controlSearch = new L.Control.Search({
					position:'topright',
					layer: markers,
					initial: false,
					zoom: 12,
					marker: false
				});

				map.addControl( controlSearch );



			////////////populate map with markers from sample data
			//	for(i in data) {
			//		var title = data[i].title,	//value searched
			//			loc = data[i].loc,		//position found
			//			marker = new L.Marker(new L.latLng(loc), {title: title} );//se property searched
			//		marker.bindPopup('title: '+ title );
			//		markersLayer.addLayer(marker);
			//	}

  };
	drawMap();
};
