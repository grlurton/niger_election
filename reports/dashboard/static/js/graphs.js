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
						sum += children[i].population;
					}
				return new L.DivIcon({html: sum, className : 'marker-cluster', iconSize: L.point(10,10)});
    }
	});
*/
			for (i = 0 ; i < records.length ; i++) {
				long = records[i]['longitude'] ;
				lat = records[i]['latitude'] ;

				popup =  '<b> Locality : </b>'+ records[i].locality +
									'<br/><b> Population : </b>' + records[i].population ;

				local_marker = L.circleMarker([lat,long]).bindPopup(popup).openPopup() ;
				local_marker.population = records[i].population ;
				markers.addLayer(local_marker) ;
			}
			map.addLayer(markers);
  };
	drawMap();
};
