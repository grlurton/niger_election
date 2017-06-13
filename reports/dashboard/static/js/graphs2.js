queue()
	.defer(d3.json,"/data")
	.await(generateVisualization);


function generateVisualization(error, data){
	console.log('Making Filters') ;
	var crossdatapoints = crossfilter(data);
	var all = crossdatapoints.groupAll();
	var byLocality = crossdatapoints.dimension(function (d) { return d.locality; });
	var byN_people = crossdatapoints.dimension(function(d){return d.n_population_2001 ; }) ;
	var byLocType = crossdatapoints.dimension(function(d){return d.loc_type ; }) ;
	var byId = crossdatapoints.dimension(function(d){return d._id ;}) ;
	var byLocation = crossdatapoints.dimension(function(p) {
		return [p.latitude,p.longitude];
	});

	var byFullLocationtemp = crossdatapoints.dimension(function(p) {
		return {"latitude":p.latitude,"longitude":p.longitude} ;
	});
	var byFullLocation = crossdatapoints.dimension(function(p) {
		return {"latitude":p.latitude,"longitude":p.longitude};
	});

	// Render the total number of datapoints
	d3.selectAll("#total").text(crossdatapoints.groupAll().reduceCount().value());


	var hide = false;
	var clicktoshow = false;

	//Automatically check the box that defines if general datapoints should be shown
	$('#checkboxgeneral').prop('checked', true);

	//function to disable-renable the general stage datapoints on the map/list
	window.filterGeneral = function(general){
		byStage.filterFunction(function (stage) {
			if (stage=='General' && general===false){
				return false;
			} else {
				return true;
			}
		});
		updateDatapoints();
		redoTagList();
		renderAll();
	};

	////////////////////////////////////////
	/// Leaflet and Mapping //
	////////////////////////////////////////
	console.log('Starting Map')
	//CREATE TILES FOR MAPPING
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

	//necessary to integrate between d3 and leaflet
	function project(x) {
		var point = map.latLngToLayerPoint(new L.LatLng(x[1], x[0]));
		return [point.x, point.y];
	}
	//the actual map created from data
	function generateMapData() {
			updateDatapoints();
	};//);
	//

	console.log('Creating markers')
	//create the leaflet marker cluster group
	var markers = L.markerClusterGroup({showCoverageOnHover:false,maxClusterRadius:20});
	var markers_list = {};

	//the datapoints on the map
	function updateDatapoints() {
		//remove all markers from the map in order to be able to do a refresh
		markers.clearLayers();
		markers_list = {};
		//for every datapoint
		byId.top(Infinity).forEach(function(p, i) {
			//create a marker at that specific position
			var marker = L.circleMarker([p.latitude,p.longitude]);
			marker.setStyle({fillOpacity: 0.5,fillColor:'#0033ff'});
			//add the marker to the map
			markers.addLayer(marker);
		});
	}
	map.addLayer(markers);

	function updateGraphs() {
		dc.barChart('#loc-type')
			.dimension(byLocType)
			.group(byLocType.group())
			.x(d3.scale.ordinal())
			.xUnits(dc.units.ordinal)
			.height(300)
			.width(250)
			.margins({top: 10, right: 50, bottom: 30, left: 40})
			.dimension(byLocType)
			.elasticY(true)
			.renderHorizontalGridLines(true)
			.xAxis().ticks(5)
	}

	//when someone click on a cluster, we want to filter so that the list of datapoints only contain the ones inside the cluster
	markers.on('clusterclick',function (a) {
		var allchild = a.layer.getAllChildMarkers();
		//if there is no more cluster underneath that cluster, we stop filtering
		if (a.layer._childClusters.length != 0 ){
			byFullLocationtemp.filterFunction(function (datapointlocation) {
				//we go through every location in crossfilter and we only keep it if it matches one of the child of the cluster we just clicked
				for (var key in allchild){
					if (datapointlocation.latitude==allchild[key].getLatLng().lat &&
					datapointlocation.longitude==allchild[key].getLatLng().lng){
						return true;
					}
				}
				return false;
			});
			updateDatapoints();
			updateGraphs() ;
			renderAll();
			}
	});


	console.log('Starting Graphs')


	// Renders the specified chart or list.
	/*
	function render(method) {
		d3.select(this).call(method);
	}
	console.log('Other Functions')
	*/
	function renderAll() {
		//list.each(render);
		//chart.each(render);
		d3.select("#active").text((all.value()));
	}


	//When clicking the Reset all filters, we show all datapoints on every visualization
	console.log('Reset Button')

	window.reset = function() {
		byFullLocation.filterAll(null);
		$('#checkboxgeneral').prop('checked', true);
		$('#checkboxlabel').show();
		byStage.filterAll(null);
		charts[0].filter(null);
		updateDatapoints();
		d3.select("#activefilter").text('');
		//recenter the map and put back at the normal zoom level
		map.setView([coordinate_x, coordinate_y],customZoom);
	};





	generateMapData();
	updateGraphs() ;
	dc.renderAll()
}
