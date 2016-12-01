queue()
	.defer(d3.json,"/data")
	.await(makeGraphs);

function makeGraphs(error, recordsJson){
	// getting data
	var records = recordsJson ;
	records.forEach( function(d,i) {
	d.ll = L.latLng(d.latitude, d.longitude);
}) ;
// ----------------------------------------------------------------------------
// BUILDING THE BASE MAP
// ----------------------------------------------------------------------------

// Creating markers and clusters layers
	//var markersLayer = new L.LayerGroup();
	//var clusterLayer = new L.MarkerClusterGroup();
  var long , lat , i , locality , popup;

	var markers = new L.markerClusterGroup({
		maxClusterRadius: 50 ,
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

	var make_markers =  function(records){
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
}
make_markers(records)

// Adding search box
var controlSearch = new L.Control.Search({
		position:'topright',
		layer: markers,
		initial: false,
		zoom: 5,
		marker: false
	});


	// creating our base layers

		// declaring map adress and attribution
	var mbAttr = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
		'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
		'Imagery © <a href="http://mapbox.com">Mapbox</a>',
		mbUrl = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpandmbXliNDBjZWd2M2x6bDk3c2ZtOTkifQ._QA7i5Mpkd_m30IGElHziw';

		// creating the different Tiles
	var grayscale   = L.tileLayer(mbUrl, {id: 'mapbox.light', attribution: mbAttr});
	var streets  = L.tileLayer(mbUrl, {id: 'mapbox.streets',   attribution: mbAttr});
	var satellite  = L.tileLayer(mbUrl, {id: 'mapbox.satellite',   attribution: mbAttr});

	var baseLayers = {
		"Grayscale": grayscale,
		"Streets": streets,
		"Satellite": satellite
	};

	// creating leaflet map
	var map = L.map('map' , {
		center: [17.6078, 8.0817],
		zoom: 5 ,
		maxZoom: 18 ,
		layers: grayscale});

	// Adding layers to a control group
	L.control.layers(baseLayers).addTo(map);
	map.addLayer(markers);
	map.addControl( controlSearch );

// ----------------------------------------------------------------------------
// Starting graphs
// ----------------------------------------------------------------------------

	// Initiating graphs
	var pop_number = dc.numberDisplay("#population-number");
	var size_settlement = dc.barChart("#size-settlement")

	// Initiating CrossFilters
	var xdata = null;
  var all = null;
  var locality = null;
	var locations = null

  // Called when dc.js is filtered (typically from user click interaction
	var onFilt = function(chart, filter) {
		updateMap(locations.top(Infinity));
	};

	// Updates the displayed map markers to reflect the crossfilter dimension passed in
	var updateMap = function(locs) {
		//clear the existing markers from the map
		markers.clearLayers() ;
		locs.forEach( function(dimensions , i) {
				popup =  '<b> Locality : </b>'+ dimensions.locality +
									'<br/><b> Population : </b>' + dimensions.n_population ;

				local_marker = L.circleMarker([dimensions.latitude,
																				dimensions.longitude] , {title: dimensions.locality , n_population: dimensions.n_population}).bindPopup(popup).openPopup() ;
				local_marker.n_population = dimensions.n_population ;
				markers.addLayer(local_marker) ;
		});
	};



	// Construct the charts
	xdata = crossfilter(records);
	all = xdata.groupAll();
	// Define the crossfilter dimensions
  locality = xdata.dimension(function (d) { return d.locality; });
	var n_people = xdata.dimension(function(d){return d.n_population ; }) ;
	var total_people = xdata.groupAll().reduceSum(function(d){return d["n_population"];});
	locations = xdata.dimension(function(d){return d.ll ;}) ;

	var dim = {} ;
	dim.locations = locations ;
	dim.locality = locality ;
	dim.n_people = n_people ;



	var binwidth = 1000;
	var group = n_people.group(function(d) { return binwidth * Math.floor(d/binwidth); });


	// setting each chart's options
	pop_number
					.formatNumber(d3.format("d"))
          .group(total_people)
					.valueAccessor(function(d){return d; })
					.formatNumber(d3.format(".3s"))
          .on("filtered", onFilt);

	size_settlement
					.x(d3.scale.linear().domain([0 , 10000]))
					.group(group)
					.dimension(n_people)
					.on("filtered", onFilt)
					//.elasticX(true)
					.xUnits(dc.units.fp.precision(binwidth));

	dc.renderAll();
};
