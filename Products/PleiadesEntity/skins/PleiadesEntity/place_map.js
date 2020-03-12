var $ = jQuery;
mapboxgl.accessToken = 'pk.eyJ1IjoiaXNhd255dSIsImEiOiJBWEh1dUZZIn0.SiiexWxHHESIegSmW8wedQ';
var bounds = new mapboxgl.LngLatBounds([[-32, 0], [160, 72]]);
var mapOptionsInit = {
  attributionControl: false,
  container: 'map',
  style: 'mapbox://styles/isawnyu/cjzy7tgy71wvr1cmj256f4dqf?fresh=true',  // force cache bypass
  // style: 'mapbox://styles/isawnyu/cjzy7tgy71wvr1cmj256f4dqf',
  maxBounds: bounds,
  renderWorldCopies: false,
};
var layerMetadata = {
  'representative-point': {
    'type': 'symbol',
    'layout': {
      'icon-image': 'circle-orange-15',
      'icon-allow-overlap': true
    }
  },
  'location-points': {
    'type': 'symbol',
    'layout': {
      'icon-image': 'crosshairs-blue-15',
      'icon-allow-overlap': true
    }
  },
  'location-polygons': {
    'type': 'fill',
    'layout': {},
    'paint': {
      'fill-color': '#5587fc',
      'fill-opacity': 0.3
    },
  },
  'connections-inbound': {
    'type': 'symbol',
    'layout': {
      'icon-image': 'interest-green-15',
      'icon-allow-overlap': true
    },
    'filter': ['==', 'inbound', ['get', 'direction']]
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
    console.debug(bounds);
    var sw = new mapboxgl.LngLat(j.bbox[0], j.bbox[1]);
    var ne = new mapboxgl.LngLat(j.bbox[2], j.bbox[3]);
    bounds = new mapboxgl.LngLatBounds(sw, ne);
    console.debug(bounds);
    map.flyTo({'center': j.reprPoint});
    map.fitBounds(bounds, {'padding': 30});
    // map.fitBounds(window.bounds);
    plotLocations(map, j);
    plotConnections(map, j);
    plotReprPoint(map, j);
  });
}

function makeLayer(map, layerTitle, features) {
  var sourceID = layerTitle.toLowerCase().replace('(', '').replace(')', '').replace(' ', '-');
  console.debug('makeLayer "' + sourceID + '"');
  console.debug(features);
  map.addSource(sourceID, {
    'type': 'geojson',
    'data': {
      'type': 'FeatureCollection',
      'features': features
    }
  });
  var layerID = 'layer-' + sourceID;
  var options = {
    'id': layerID,
    'type': layerMetadata[sourceID]['type'],
    'source': sourceID,
    'layout': layerMetadata[sourceID]['layout']
  }
  if ('filter' in layerMetadata[sourceID]) {
    options['filter'] = layerMetadata[sourceID]['filter'];
  }
  if ('paint' in layerMetadata[sourceID]) {
    options['paint'] = layerMetadata[sourceID]['paint'];
  }
  map.addLayer(options);
  map.on('click', layerID, function(e) {
    feature = e.features[0]
    snippet = '<dd>' + feature.properties.title + '</dd>';
    if (feature.properties.descripton != '') {
      snippet += '<dt>' + feature.properties.description + '</dt>'
    }
    new mapboxgl.Popup()
    .setLngLat(e.lngLat)
    .setHTML(snippet)
    .addTo(map);
  });
  map.on('mouseenter', layerID, function() {
    map.getCanvas().style.cursor = 'pointer';
  });
  map.on('mouseleave', layerID, function() {
    map.getCanvas().style.cursor = '';
  });  
}

function plotConnections(map, j) {
  let outbound = j.connections.map(a => a.connectsTo);
  var coords;
  $.getJSON($('link[rel="connections"][type="application/json"]').attr('href'),
  function (cnxj) {
    cnxj.features.forEach(function(connection) {
      var predicate = connection.properties.link;
      if (outbound.indexOf(predicate) != -1) {
        connection.properties['direction'] = 'outbound';
      } else {
        connection.properties['direction'] = 'inbound';
        coords = connection.geometry.coordinates;
        if (!bounds.contains(coords)) {
          here = new mapboxgl.LngLat(coords[0], coords[1]);
          bounds.extend(here);
        }
      }
    });
    makeLayer(map, 'Connections Inbound', cnxj.features);
    map.fitBounds(bounds, {'padding': 30});
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
  features = [
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
  makeLayer(map, 'Representative Point', features);       
}

