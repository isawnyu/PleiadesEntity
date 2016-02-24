PLZoom = L.Control.Zoom.extend({
    onAdd: function (map) {
        var className = 'leaflet-control-zoom',
            container = L.DomUtil.create('div', className);
        this._map = map;
        this._createButton('Zoom reset', 
            className + '-reset', 
            container, 
            this._zoomReset, 
            this );
        this._createButton('Zoom in', 
            className + '-in', 
            container, 
            this._zoomIn, 
            this );
        this._createButton('Zoom out', 
            className + '-out', 
            container, 
            this._zoomOut, 
            this );
        return container;
    },

    _zoomReset: function (e) {
        this._map.fitBounds(this.options.initialBounds); 
    },

    _zoomIn: function (e) {
        this._map.zoomIn(e.shiftKey ? 3 : 1);
    },

    _zoomOut: function (e) {
        this._map.zoomOut(e.shiftKey ? 3 : 1);
    },

    _createButton: function (title, className, container, fn, context) {
        var link = L.DomUtil.create('a', className, container);
        link.href = '#';
        link.title = title;
        L.DomEvent
            .on(link, 'click', L.DomEvent.stopPropagation)
            .on(link, 'mousedown', L.DomEvent.stopPropagation)
            .on(link, 'dblclick', L.DomEvent.stopPropagation)
            .on(link, 'click', L.DomEvent.preventDefault)
            .on(link, 'click', fn, context);
        return link;
    }
});

pl_zoom = function (options) {
    return new PLZoom(options);
};

function getJSON(rel) {
  var documentNode = document;
  var linkNode = documentNode.evaluate(
      '//*[@rel="' + rel + '" and @type="application/json"]',
      documentNode,
      null,
      XPathResult.FIRST_ORDERED_NODE_TYPE,
      null).singleNodeValue;
  if (linkNode != null) {
    var uri = linkNode.getAttribute("href");
    var json = unescape(uri.split(',').pop());
    return JSON.parse(json);
  }
  else {
    return null;
  }
}

var bounds = null;
var baselineBounds = null;
var reprPoint = null;

/* parse place spatial info from JSON URI in the place page */
var where = getJSON("where");
if (where && where.bbox) {
  bounds = L.latLngBounds([
    [where.bbox[1], where.bbox[0]],
    [where.bbox[3], where.bbox[2]] ]).pad(0.10);
}
if (where && where.reprPoint) {
  console.info('reprPoint[0]: ' + where.reprPoint[0])
  console.info('reprPoint[1]: ' + where.reprPoint[1])
  reprPoint = L.latLng(where.reprPoint[1], where.reprPoint[0])
  console.info('lat: ' + reprPoint.lat)
  console.info('lng: ' + reprPoint.lng)
}

/* parse place spatial info from JSON uri in the baseline place (if this is a working copy) */
var baselineWhere = getJSON("baseline-where");
if (baselineWhere && baselineWhere.bbox) {
  baselineBounds = L.latLngBounds([
    [baselineWhere.bbox[1], baselineWhere.bbox[0]],
    [baselineWhere.bbox[3], baselineWhere.bbox[2]] ]).pad(0.10);
  if (bounds) {
    bounds.extend(baselineBounds);
  }
  else { bounds = baselineBounds; }
}

/* If there's no spatial context at all, set large bounds. */
if (!bounds) { bounds = L.latLngBounds([[20.0, -5.0], [50.0, 45.0]]); }

var map = L.map('map', {attributionControl: false});
/* map.setView(bounds.getCenter(), Math.min(map.getBoundsZoom(bounds), 101), true); */
map.fitBounds(bounds, {maxZoom: 7});
L.control.attribution({prefix: false, position: 'bottomright'}).addTo(map);
pl_zoom({initialBounds: bounds}).addTo(map);

var awmcterrain = L.tileLayer(
    'https://api.tiles.mapbox.com/v4/isawnyu.map-knmctlkh/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiaXNhd255dSIsImEiOiJBWEh1dUZZIn0.SiiexWxHHESIegSmW8wedQ', {
        attribution: 'Powered by <a href="http://leafletjs.com/">Leaflet</a> and <a href="https://www.mapbox.com/">Mapbox</a>. Map base by <a title="Ancient World Mapping Center (UNC-CH)" href="http://awmc.unc.edu">AWMC</a>, 2014 (cc-by-nc).',
        maxZoom: 12
        });
awmcterrain.addTo(map);

/* Not added by default, only through user control action */
var terrain = L.tileLayer(
    'https://api.tiles.mapbox.com/v4/isawnyu.map-p75u7mnj/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiaXNhd255dSIsImEiOiJBWEh1dUZZIn0.SiiexWxHHESIegSmW8wedQ', {
        attribution: 'Powered by <a href="http://leafletjs.com/">Leaflet</a> and <a href="https://www.mapbox.com/">Mapbox</a>. Map base by <a title="Institute for the Study of the Ancient World (ISAW)" href="http://isaw.nyu.edu">ISAW</a>, 2014 (cc-by).'
        });

var streets = L.tileLayer(
    'https://api.tiles.mapbox.com/v4/isawnyu.map-zr78g89o/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiaXNhd255dSIsImEiOiJBWEh1dUZZIn0.SiiexWxHHESIegSmW8wedQ', {
        attribution: 'Powered by <a href="http://leafletjs.com/">Leaflet</a> and <a href="https://www.mapbox.com/">Mapbox</a>. Map base by <a title="Institute for the Study of the Ancient World (ISAW)" href="http://isaw.nyu.edu">ISAW</a>, 2014 (cc-by).'
        });

var imperium = L.tileLayer(
    'http://dare.ht.lu.se/tiles/imperium/{z}/{x}/{y}.png', {
        attribution: 'Powered by <a href="http://leafletjs.com/">Leaflet</a>. Map base: <a href="http://dare.ht.lu.se/" title="Digital Atlas of the Roman Empire, Department of Archaeology and Ancient History, Lund University, Sweden">DARE</a>, 2015 (cc-by-sa).',
        maxZoom: 11
        });

var bluemarble = L.GIBSLayer(
    'BlueMarble_ShadedRelief_Bathymetry', {
      transparent: false,
      attribution: 'Powered by <a href="http://leafletjs.com/">Leaflet</a>, <a href="https://github.com/aparshin/leaflet-GIBS">Leaflet-GIBS</a>, and <a href="https://earthdata.nasa.gov/gibs" title="We acknowledge the use of imagery provided by services from the Global Imagery Browse Services (GIBS), operated by the NASA/GSFC/Earth Science Data and Information System (ESDIS, https://earthdata.nasa.gov) with funding provided by NASA/HQ.">NASA EOSDIS GIBS</a>, 2008-present.',
      });

var baseLayers = {
    "Ancient Terrain (default)": awmcterrain,
    "Modern Terrain": terrain,
    "Modern Streets": streets,
    "Roman Empire": imperium,
    "NASA Blue Marble": bluemarble,
}

var reprMark = L.circleMarker(
  reprPoint, {
    stroke: true,
    color: '#333',
    fill: true,
    fillColor: '#FFA500',
    fillOpacity: 1,
    radius: 7,
    });

var awmcJSON = getJSON()

var overlays = {
    "Representative point": reprMark,
}

L.control.layers(baseLayers, overlays).addTo(map);

var target = null;

/* set up icons for vector layers */

var connectionIcon = new L.Icon({
    iconUrl: "http://pleiades.stoa.org/images/pmapi/21/connection-green.png",
    iconSize:     [21, 26],
    iconAnchor:   [12, 28],
    popupAnchor:  [0, -23]
  });

var locationIcon = new L.Icon({
    iconUrl: "http://pleiades.stoa.org/images/pmapi/32/location-blue.png",
    iconSize:     [32, 37],
    iconAnchor:   [16, 35],
    popupAnchor:  [0, -33]
  });

var baselineLocationIcon = new L.Icon({
    iconUrl: "http://pleiades.stoa.org/images/pmapi/21/location-gray.png",
    iconSize:     [21, 26],
    iconAnchor:   [12, 28],
    popupAnchor:  [0, -23]
  });

/* add vector layers */

/* locations in the current place object */
if (where) {
  L.geoJson(where, {
    pointToLayer: function (feature, latlng) {
        return L.marker(latlng, {icon: locationIcon, zIndexOffset: 1000 });
    },
    style: function(f) {
        return {
          color: '#5587fc',
          opacity: 1,
          weight: 2,
          fill: true,
          fillColor: '#5587fc',
          fillOpacity: 0.2,
        }
    },
    onEachFeature: function (f, layer) {
      layer.bindPopup(
        '<dt><a href="' 
        + f.properties.link + '">' + f.properties.title + '</a></dt>'
        + '<dd>' + f.properties.description + '</dd>' );
        if (jQuery("h1").text() == f.properties.title) { target = layer; }
    }
  }).addTo(map);
}

/* locations in the baseline (if this is a working copy) */
/* color: gray (555555) */
if (baselineWhere) {
  L.geoJson(baselineWhere, {
    pointToLayer: function (feature, latlng) {
        return L.marker(latlng, {icon: baselineLocationIcon, zIndexOffset: 100 });
    },
    style: function(f) {
        return {
          color: '#555555',
          opacity: 1,
          weight: 2,
          fill: true,
          fillColor: '#555555',
          fillOpacity: 0.2,
        }
    },
    onEachFeature: function (f, layer) {
      layer.bindPopup(
        '<dt><a href="' 
        + f.properties.link + '">' + f.properties.title + '</a></dt>'
        + '<dd>' + f.properties.description + '</dd>' );
    }
  }).addTo(map);
}

/* connections */
/* NB: there's only JSON for all connections, so we can't 
  distinguish between from and to */
var connections = getJSON("connections");
if (connections) {
  L.geoJson(connections, {
    filter: function (f, layer) {
      return f.type == 'Feature';
    },
    pointToLayer: function (feature, latlng) {
        return L.marker(latlng, {icon: connectionIcon, zIndexOffset: 10 });
    },    
    style: function(f) {
        return {
          color: '#55cb4f',
          opacity: 1,
          weight: 2,
          fill: true,
          fillColor: '#55cb4f',
          fillOpacity: 0.2,
        }
    },
    onEachFeature: function (f, layer) {
      layer.bindPopup(
        '<dt><a href="' 
        + f.properties.link + '">' + "Connection: " + f.properties.title + '</a></dt>'
        + '<dd>' + f.properties.description + '</dd>' );
        if (jQuery("h1").text() == f.properties.title) { target = layer; }
    }
  }).addTo(map);
}

if (target != null) {
  target.openPopup();
}


