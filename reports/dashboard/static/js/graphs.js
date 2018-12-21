queue()
    .defer(d3.json, "/data")
    .await(makeGraphs);


function makeGraphs(error, data) {
    data.forEach(function(d, i) {
        d.ll = L.latLng(d.latitude, d.longitude);
    });
    // getting data
    var records = data;
    // Construct the charts
    var xdata = crossfilter(records);
    // var all = xdata.groupAll();
    var groupname = "marker-select";
    // ----------------------------------------------------------------------------
    // BUILDING THE BASE MAP
    // ----------------------------------------------------------------------------

    // Creating markers and clusters layers
    var long, lat, i, locality, popup;

    var markers = new L.markerClusterGroup({
        maxClusterRadius: 50,
        chunkedLoading: true,
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
            } else if (sum < 500000) {
                c += 'large';
            } else if (sum < 1000000) {
                c += 'semi-large';
            } else {
                c += 'very-large';
            }
            return new L.DivIcon({
                html: '<div><span><b>' + sum + '</b></span></div>',
                className: 'marker-cluster' + c,
                iconSize: L.point(40, 40)
            });
        }
    });

    for (i = 0; i < records.length; i++) {
        long = records[i]['longitude'];
        lat = records[i]['latitude'];
        locality = records[i].locality;
        console.log(locality);
        n_population_2001 = records[i].n_population_2001;

        popup = '<b> Locality : </b>' + locality +
            '<br/><b> Population : </b>' + n_population_2001;
        local_marker = L.circleMarker([lat, long], {
            title: locality,
            n_population_2001: n_population_2001
        }).bindPopup(popup).openPopup();
        local_marker.n_population_2001 = n_population_2001;
        markers.addLayer(local_marker);
    }

    // Adding search box
    var controlSearch = new L.Control.Search({
        position: 'topright',
        layer: markers,
        initial: false,
        zoom: 15,
        marker: false
    });


    // creating our base layers

    // declaring map adress and attribution
    // creating the different Tiles
    var grayscale = L.esri.basemapLayer('Streets') ;
    var streets = L.tileLayer('http://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
        maxZoom: 20,
        attribution: '&copy; Openstreetmap France | &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    });
    var satellite = L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    });

    var baseLayers = {
        "Grayscale": grayscale,
        "Streets": streets,
        "Satellite": satellite
    };

    // creating leaflet map
    var map = L.map('map', {
        center: [17.6078, 8.0817],
        zoom: 5,
        layers: satellite
    });

    // Adding layers to a control group
    L.control.layers(baseLayers).addTo(map);
    map.addLayer(markers);
    map.addControl(controlSearch);

    // ----------------------------------------------------------------------------
    // Starting graphs
    // ----------------------------------------------------------------------------

    // Initiating graphs
    console.log("starting Graphing !");
    var pop_number = dc.numberDisplay("#population-number");
    var size_settlement = dc.barChart("#size-settlement") ;
    var data_comparison = dc.scatterPlot("#data-comparison") ;
    var locality_types = dc.barChart("#loc-type") ;

    // Called when dc.js is filtered
    var onFilt = function(chart, filter) {
        updateMap(locations.top(Infinity));
    };

    // Updates the displayed map markers to reflect the crossfilter dimension passed in
    console.log('Adding interactivity') ;
    var updateMap = function(locs) {
        //clear the existing markers from the map
        markers.clearLayers();
        locs.forEach(function(dimensions, i) {
            popup = '<b> Locality : </b>' + dimensions.locality +
                '<br/><b> Population : </b>' + dimensions.n_population_2001;

            local_marker = L.circleMarker(
                [dimensions.latitude, dimensions.longitude], {
                    title: dimensions.locality,
                    n_population_2001: dimensions.n_population_2001
                }).bindPopup(popup).openPopup();
            local_marker.n_population_2001 = dimensions.n_population_2001;
            markers.addLayer(local_marker);
        });
    };

    // Define the crossfilter dimensions
    console.log('Crossfilter 1')
    var locality = xdata.dimension(function(d) {
        return d.locality;
    });
    console.log('Crossfilter 2')
    var n_people = xdata.dimension(function(d) {
        return d.n_population_2001;
    });
    console.log('Crossfilter 3')
    var total_people = xdata.groupAll().reduceSum(function(d) {
        return d["n_population_2001"];
    });
    console.log('Crossfilter 4')
    var locations = xdata.dimension(function(d) {
        return d.ll;
    });
    console.log('Crossfilter 5');
    var voter = xdata.dimension(function(d) {
        return [d.n_population_2001, d.n_population_2012];
    });
    var group1 = voter.group();

    console.log('Crossfilter 6');
    var locType = xdata.dimension(function(d) {
        return d.loc_type ;
    });
    var locTypeGroup = locType.group();

    var binwidth = 1000;
    var group = n_people.group(function(d) {
        return binwidth * Math.floor(d / binwidth);
    });


    // setting each chart's options
    console.log('starting charts');
    console.log('chart 1');
    pop_number
        .formatNumber(d3.format("d"))
        .group(total_people)
        .valueAccessor(function(d) {
            return d;
        })
        .formatNumber(d3.format(".3s"))
        .on("filtered", onFilt);

    console.log('chart 2');
    size_settlement
        .x(d3.scale.linear().domain([0, 10000]))
        .height(300)
        .width(250)
        .margins({
            top: 10,
            right: 50,
            bottom: 30,
            left: 40
        })
        .group(group)
        .dimension(n_people)
        .on("filtered", onFilt)
        .elasticY(true)
        .xUnits(dc.units.fp.precision(binwidth))
        .renderHorizontalGridLines(true)
        .xAxis().ticks(5);

    console.log('chart 3');
    data_comparison
        .width(250)
        .height(300)
        .x(d3.scale.linear().domain([0, 10000]))
        .margins({
            top: 10,
            right: 50,
            bottom: 30,
            left: 40
        })
        .elasticY(true)
        .yAxisLabel("RENALOC")
        .xAxisLabel("RENACOM")
        .clipPadding(10)
        .on("filtered", onFilt)
        .dimension(voter)
        .excludedColor('#ddd')
        .group(group1)
        .xAxis().ticks(5);

    console.log('chart 4');
    locality_types
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .height(300)
        .width(250)
        .margins({
            top: 10,
            right: 50,
            bottom: 30,
            left: 40
        })
        .dimension(locType)
        .on("filtered", onFilt)
        .group(locTypeGroup)
        .elasticY(true)
        .renderHorizontalGridLines(true)
        .xAxis().ticks(5);

    dc.renderAll();
};
