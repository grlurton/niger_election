queue()
	.defer(d3.json,"/data")
	.await(makeGraphs);


function makeGraphs(error, recordsJson){
	var records = recordsJson ;
	var chart_rec = recordsJson ; 

	//Clean data 
	chart_rec.forEach(function(d) {
		d["longitude"] = +d["longitude"];
		d["latitude"] = +d["latitude"];
	});

	//Create a Crossfilter instance
	var ndx = crossfilter(chart_rec)

	//Define Dims 
	var popDim = ndx.dimension(function(d){ return d['n_population'];}) ;
	var allDim = ndx.dimension(function(d) {return d;});

	var popGroup = popDim.group();
	var all = ndx.groupAll();

	//Charts 
	var popChart = dc.rowChart("#population-row-chart");

	popChart
		.width(300)
        .height(100)
        .dimension(popDim)
        //.group(popGroup)
        //.ordering(function(d) { return -d.value })
        //.colors(['#6baed6'])
        //.elasticX(true)
        //.xAxis().ticks(4);
	// Add Map
	

	var drawMap = function(d){

		var cities = new L.LayerGroup();

	


	var mbAttr = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
			'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
			'Imagery © <a href="http://mapbox.com">Mapbox</a>',
		mbUrl = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpandmbXliNDBjZWd2M2x6bDk3c2ZtOTkifQ._QA7i5Mpkd_m30IGElHziw';

	var grayscale   = L.tileLayer(mbUrl, {id: 'mapbox.light', attribution: mbAttr});
	var streets  = L.tileLayer(mbUrl, {id: 'mapbox.streets',   attribution: mbAttr});
	var satellite  = L.tileLayer(mbUrl, {id: 'mapbox.satellite',   attribution: mbAttr});
	var map = L.map('map', {
		center: [39.73, -104.99],
		zoom: 10,
		layers: [grayscale, cities, satellite]
	});

	var baseLayers = {
		"Grayscale": grayscale,
		"Streets": streets,
		"Satellite": satellite
	};

	var overlays = {
		"Cities": cities
	};

	L.control.layers(baseLayers, overlays).addTo(map);
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
