var $ = jQuery;
mapboxgl.accessToken = 'pk.eyJ1IjoiaXNhd255dSIsImEiOiJBWEh1dUZZIn0.SiiexWxHHESIegSmW8wedQ';
var bounds = new mapboxgl.LngLatBounds([[-32, 0], [160, 72]]);
var mapOptionsInit = {
  attributionControl: false,
  container: 'map',
  maxZoom: 12,
  style: 'mapbox://styles/isawnyu/cjzy7tgy71wvr1cmj256f4dqf?fresh=true',
  maxBounds: bounds,
  renderWorldCopies: false,
};
var layerMetadata = {
  'representative-point': {
    'type': 'symbol',
    'layout': {
      'icon-image': 'circle-orange-15'
    },
    'paint': {}
  },
  'location-points': {
    'type': 'symbol',
    'layout': {
      'icon-image': 'crosshairs-blue-15'
    },
    'paint': {}
  },
  'location-polygons': {
    'type': 'fill',
    'layout': {},
    'paint': {
      'fill-color': '#5587fc',
      'fill-opacity': 0.2
    }
  }
}

var map = new mapboxgl.Map(mapOptionsInit); 
map = map.addControl(new mapboxgl.AttributionControl({
  compact: true, 
}));
map = map.addControl(new mapboxgl.NavigationControl({
  showCompass: false,
}));
map = map.addControl(new mapboxgl.ScaleControl());
if (map.loaded()) {
  populateMap(map);
} else {
  map.on('load', () => populateMap(map));
}

function populateMap(map) {
  var jurl = $('link[rel="canonical"]').attr('href') + '/json'
  $.getJSON(jurl, function(j) {
    // mapPoint(map, j.reprPoint, 'reprPoint')
    bounds = new mapboxgl.LngLatBounds(j.bbox);
    map.flyTo({'center': j.reprPoint});
    map.fitBounds(bounds);
    plotReprPoint(map, j);
    plotLocations(map, j);
    // map.fitBounds(bounds, {'padding': 20});
    // plotConnections(map, j, bounds);
  });
}

function makeLayer(map, layerTitle, features) {
  layerID = layerTitle.toLowerCase().replace(' ', '-');
  map.addSource(layerID, {
    'type': 'geojson',
    'data': {
      'type': 'FeatureCollection',
      'features': features
    }
  });
  map.addLayer({
    'id': layerID,
    'type': layerMetadata[layerID]['type'],
    'source': layerID,
    'layout': layerMetadata[layerID]['layout'],
    'paint': layerMetadata[layerID]['paint']
  });
}

function plotLocations(map, j) {
  var pointFeatures = Array();
  var polyFeatures = Array();
  j.locations.forEach(function(location) {
    var geoType = location.geometry.type;
    var feature = {
      'type': 'Feature',
      'geometry': location.geometry,
      'properties': {
        'title': location.title,
        'description': location.description
      }
    }
    if (geoType == 'Point') {
      pointFeatures.push(feature);
    } else if (geoType == 'Polygon') {
      polyFeatures.push(feature);
    }
  });
  makeLayer(map, 'Location Polygons', polyFeatures);
  makeLayer(map, 'Location Points', pointFeatures);
}

function plotReprPoint(map, j) {
  map.addSource('reprPoint', {
    'type': 'geojson',
    'data': {
      'type': 'FeatureCollection',
      'features': [
        {
          'type': 'Feature',
          'geometry': {
            'type': 'Point',
            'coordinates': j.reprPoint
          },
          'properties': {
            'title': 'Representative point for ' + j.title,
            'icon': 'repr-point'
          }
        }
      ]
    }
  });
  map.addLayer({
    'id': 'reprPoint',
    'type': 'symbol',
    'source': 'reprPoint',
    'layout': {
      'icon-image': 'circle-orange-15'
    }
  });
  map.on('click', 'reprPoint', function(e) {
    snippet = '<dd>Representative Point</dd>';
    new mapboxgl.Popup()
      .setLngLat(j.reprPoint)
      .setHTML(snippet)
      .addTo(map);
  });
  map.on('mouseenter', 'reprPoint', function() {
    map.getCanvas().style.cursor = 'pointer';
  });
  map.on('mouseleave', 'reprPoint', function() {
    map.getCanvas().style.cursor = '';
  });                
}
