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
    return jq.parseJSON(json);
  }
  else {
    return null;
  }
}

var bounds = null;
var baselineBounds = null;

var where = getJSON("where");
if (where && where.bbox) {
  bounds = L.latLngBounds([
    [where.bbox[1], where.bbox[0]],
    [where.bbox[3], where.bbox[2]] ]).pad(0.10);
}

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
map.setView(bounds.getCenter(), Math.min(map.getBoundsZoom(bounds), 11), true);
L.control.attribution({prefix: false, position: 'bottomright'}).addTo(map);
pl_zoom({initialBounds: bounds}).addTo(map);

var awmcterrain = L.tileLayer(
    'https://api.tiles.mapbox.com/v4/isawnyu.map-knmctlkh/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiaXNhd255dSIsImEiOiJBWEh1dUZZIn0.SiiexWxHHESIegSmW8wedQ', {
        attribution: 'Powered by <a href="http://leafletjs.com/">Leaflet</a> and <a href="https://www.mapbox.com/">Mapbox</a>. Map base by <a title="Ancient World Mapping Center (UNC-CH)" href="http://awmc.unc.edu">AWMC</a>, 2014 (cc-by-nc).'
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
    'http://pelagios.dme.ait.ac.at/tilesets/imperium//{z}/{x}/{y}.png', {
        attribution: 'Powered by <a href="http://leafletjs.com/">Leaflet</a>. Map base: <a href="http://pelagios.dme.ait.ac.at/maps/greco-roman/about.html">Pelagios</a>, 2012; Data: NASA, OSM, Pleiades, DARMC (cc-by).',
        maxZoom: 11
        });

L.control.layers({
    "Ancient Terrain (default)": awmcterrain,
    "Modern Terrain": terrain,
    "Modern Streets": streets,
    "Roman Empire": imperium,
    }).addTo(map);

var target = null;

var placeIcon = new L.Icon({
    iconUrl: "http://atlantides.org/images/justice-blue.png",
    iconSize:     [32, 37],
    iconAnchor:   [16, 37]
  });

if (where) {
  L.geoJson(where, {
    onEachFeature: function (f, layer) {
      layer.bindPopup(
        '<dt><a href="' 
        + f.properties.link + '">' + f.properties.title + '</a></dt>'
        + '<dd>' + f.properties.description + '</dd>' );
        if (jq("h1").text() == f.properties.title) { target = layer; }
    }
  }).addTo(map);
}

if (baselineWhere) {
  L.geoJson(baselineWhere, {
    onEachFeature: function (f, layer) {
      layer.bindPopup(
        '<dt><a href="' 
        + f.properties.link + '">' + f.properties.title + '</a></dt>'
        + '<dd>' + f.properties.description + '</dd>' );
    }
  }).addTo(map);
}

var connections = getJSON("connections");

if (connections) {
  L.geoJson(connections, {
    filter: function (f, layer) {
      return f.type == 'Feature';
    },
    onEachFeature: function (f, layer) {
      layer.bindPopup(
        '<dt><a href="' 
        + f.properties.link + '">' + f.properties.title + '</a></dt>'
        + '<dd>' + f.properties.description + '</dd>' );
        if (jq("h1").text() == f.properties.title) { target = layer; }
    }
  }).addTo(map);
}

if (target != null) {
  target.openPopup();
}


