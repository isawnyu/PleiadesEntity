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
var where = getJSON("where");
if (where && where.bbox) {
  bounds = L.latLngBounds([
    [where.bbox[1], where.bbox[0]],
    [where.bbox[3], where.bbox[2]] ]).pad(0.10);
}
else { bounds = L.latLngBounds([[20.0, -5.0], [50.0, 45.0]]); }

var map = L.map('map', {zoomControl: false}).fitBounds(bounds);
if (map.getZoom() > 11) { 
  map.setZoom(11);
  bounds = map.getBounds();
}
pl_zoom({initialBounds: bounds}).addTo(map);

var terrain = L.tileLayer(
    'http://api.tiles.mapbox.com/v3/sgillies.map-ac5eaoks/{z}/{x}/{y}.png', {
        attribution: "ISAW, 2012"
        });
terrain.addTo(map);

/* Not added by default, only through user control action */
var streets = L.tileLayer(
    'http://api.tiles.mapbox.com/v3/sgillies.map-pmfv2yqx/{z}/{x}/{y}.png', {
        attribution: "ISAW, 2012"
        });

var imperium = L.tileLayer(
    'http://pelagios.dme.ait.ac.at/tilesets/imperium//{z}/{x}/{y}.png', {
        attribution: 'Tiles: <a href="http://pelagios-project.blogspot.com/2012/09/a-digital-map-of-roman-empire.html">Pelagios</a>, 2012; Data: NASA, OSM, Pleiades, DARMC',
        maxZoom: 11
        });

L.control.layers({
    "Terrain (default)": terrain,
    "Streets": streets,
    "Imperium": imperium,
    }).addTo(map);

var target = null;

L.geoJson(where, {
    onEachFeature: function (f, layer) {
      layer.bindPopup(
        '<dt><a href="' 
        + f.properties.link + '">' + f.properties.title + '</a></dt>'
        + '<dd>' + f.properties.description + '</dd>' );
        if (jq("h1").text() == f.properties.title) { target = layer; }
    }
}).addTo(map);

if (target != null) {
  target.openPopup();
}


