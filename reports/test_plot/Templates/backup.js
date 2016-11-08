<script type="text/javascript">
  // The first parameter are the coordinates of the center of the map
  // The second parameter is the zoom level
  var map = L.map('map').setView([17.6078, 8.0817], 5);
  
  // {s}, {z}, {x} and {y} are placeholders for map tiles
  // {x} and {y} are the x/y of where you are on the map
  // {z} is the zoom level
  // {s} is the subdomain of cartodb
      var layer = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
  });
  
  // Now add the layer onto the map
  map.addLayer(layer);
  // adding marker
  L.marker([16.31, 8.067]).addTo(map)
  .bindPopup("<strong>Amalaba</strong><strong> </strong><strong>Population : 704</strong>").openPopup
  L.marker([15.653, 8.085]).addTo(map)
  .bindPopup("<strong>AKOUEL (AKOYAL)</strong><strong>Population : 129</strong>").openPopup();
  
  </script>