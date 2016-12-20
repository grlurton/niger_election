queue()
	.defer(d3.json,"/data")
	.await(makeGraphs);


function makeGraphs(error, recordsJson){
	recordsJson.forEach( function(d,i) {
		d.ll = L.latLng(d.latitude, d.longitude);
	}) ;
	// getting data
	var records = recordsJson ;
	// Construct the charts
	var xdata = crossfilter(records);
	// var all = xdata.groupAll();
	var groupname = "marker-select";
// ----------------------------------------------------------------------------
// BUILDING THE BASE MAP
// ----------------------------------------------------------------------------

// Creating markers and clusters layers
	var long , lat , i , locality , popup;

	var markers = new L.markerClusterGroup({
		maxClusterRadius: 50 ,
		chunkedLoading: true ,
		// Custom function to display count of people in cluster
		iconCreateFunction: function(cluster) {
			var children = cluster.getAllChildMarkers();
			var sum = 0;
			for (var i = 0; i < children.length; i++) {
				sum += children[i].n_population_2001;
			}

			var c = ' marker-cluster-';

			if (sum < 50000) {
					c += 'small';
			} else if (sum < 10000) {
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
		locality = records[i].locality ;
		n_population_2001 = records[i].n_population_2001 ;

		popup =  '<b> Locality : </b>'+ locality +
				'<br/><b> Population : </b>' + n_population_2001 ;
		local_marker = L.circleMarker([lat,long] ,
										{title: locality ,
										n_population_2001: n_population_2001}).bindPopup(popup).openPopup() ;
		local_marker.n_population_2001 =n_population_2001 ;
		markers.addLayer(local_marker) ;
	}

// Adding search box
	var controlSearch = new L.Control.Search({
		position:'topright',
		layer: markers,
		initial: false,
		zoom: 15,
		marker: false
	});


	// creating our base layers

	// declaring map adress and attribution
	var mbAttr = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
		'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
		'Imagery © <a href="http://mapbox.com">Mapbox</a>',
		mbUrl = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpandmbXliNDBjZWd2M2x6bDk3c2ZtOTkifQ._QA7i5Mpkd_m30IGElHziw';

	// creating the different Tiles
	var grayscale   = L.tileLayer(mbUrl,
		{id: 'mapbox.light', attribution: mbAttr});
	var streets  = L.tileLayer(mbUrl,
		{id: 'mapbox.streets',   attribution: mbAttr});
	var satellite  = L.tileLayer(mbUrl,
		{id: 'mapbox.satellite',   attribution: mbAttr});

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
	var data_comparison = dc.scatterPlot("#data-comparison")
	var locality_types = dc.barChart("#loc-type")

// Called when dc.js is filtered
	var onFilt = function(chart, filter) {
		updateMap(locations.top(Infinity));
	};

	// Updates the displayed map markers to reflect the crossfilter dimension passed in
	var updateMap = function(locs) {
		//clear the existing markers from the map
		markers.clearLayers() ;
		locs.forEach( function(dimensions , i) {
			popup =  '<b> Locality : </b>'+ dimensions.locality +
			'<br/><b> Population : </b>' + dimensions.n_population_2001 ;

		local_marker = L.circleMarker(
			[dimensions.latitude,dimensions.longitude] ,
			{title: dimensions.locality ,
				n_population_2001: dimensions.n_population_2001}).bindPopup(popup).openPopup() ;
				local_marker.n_population_2001 = dimensions.n_population_2001 ;
				markers.addLayer(local_marker) ;
		});
	};

	// Define the crossfilter dimensions
	var locality = xdata.dimension(function (d) { return d.locality; });
	var n_people = xdata.dimension(function(d){return d.n_population_2001 ; }) ;
	var total_people = xdata.groupAll().reduceSum(function(d){return d["n_population_2001"];});
	var locations = xdata.dimension(function(d){return d.ll ;}) ;
	var voter = xdata.dimension(function(d){return [d.n_population_2001 , d.n_population_2012] ; });
	var group1 = voter.group() ;

	var locType = xdata.dimension(function(d){
		return d.loc_type}) ;
	var locTypeGroup = locType.group() ;

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
		.height(300)
		.width(250)
		.margins({top: 10, right: 50, bottom: 30, left: 40})
		.group(group)
		.dimension(n_people)
		.on("filtered", onFilt)
		.elasticY(true)
		.xUnits(dc.units.fp.precision(binwidth))
		.renderHorizontalGridLines(true)
		.xAxis().ticks(5);

	data_comparison
		.width(250)
		.height(300)
		.x(d3.scale.linear().domain([0, 10000]))
		.margins({top: 10, right: 50, bottom: 30, left: 40})
		.elasticY(true)
		.yAxisLabel("RENALOC")
		.xAxisLabel("RENACOM")
		.clipPadding(10)
		.on("filtered", onFilt)
		.dimension(voter)
		.excludedColor('#ddd')
		.group(group1)
		.xAxis().ticks(5);

	locality_types
		.x(d3.scale.ordinal())
		.xUnits(dc.units.ordinal)
		.height(300)
		.width(250)
		.margins({top: 10, right: 50, bottom: 30, left: 40})
		.dimension(locType)
		.on("filtered", onFilt)
		.group(locTypeGroup)
		.elasticY(true)
		.renderHorizontalGridLines(true)
		.xAxis().ticks(5);

	dc.renderAll();
};
