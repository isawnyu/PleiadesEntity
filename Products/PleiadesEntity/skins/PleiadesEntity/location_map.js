var L, PLZoom;
var $ = jQuery;
var target = null;

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

var pl_zoom = function (options) {
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
  if (linkNode !== null) {
    var uri = linkNode.getAttribute("href");
    var json = unescape(uri.split(',').pop());
    return JSON.parse(json);
  }
  else {
    return null;
  }
}

$(function () {
  var bounds = null;
  var baselineBounds = null;
  var map = L.map('map', {attributionControl: false});
  L.control.attribution({prefix: false, position: 'bottomright'}).addTo(map);

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
      'http://pelagios.dme.ait.ac.at/tilesets/imperium//{z}/{x}/{y}.png', {
          attribution: 'Powered by <a href="http://leafletjs.com/">Leaflet</a> and <a href="https://www.mapbox.com/">Mapbox</a>. Map base: <a href="http://pelagios.dme.ait.ac.at/maps/greco-roman/about.html">Pelagios</a>, 2012; Data: NASA, OSM, Pleiades, DARMC (cc-by).',
          maxZoom: 11
          });

  var baseLayers = {
      "Ancient Terrain (default)": awmcterrain,
      "Modern Terrain": terrain,
      "Modern Streets": streets,
      "Roman Empire": imperium,
  };

  var overlays = null;
  L.control.layers(baseLayers, overlays).addTo(map);

  /* set up icons for vector layers */
  var locationIcon = new L.Icon({
      iconUrl: portal_url + '/map_icons/location-blue.png',
      iconSize:     [32, 37],
      iconAnchor:   [16, 35],
      popupAnchor:  [0, -33]
    });

  var baselineLocationIcon = new L.Icon({
      iconUrl: portal_url + '/map_icons/location-gray.png',
      iconSize:     [21, 26],
      iconAnchor:   [12, 28],
      popupAnchor:  [0, -23]
  });

  function rebound() {
    /* If there's no spatial context at all, set large bounds. */
    if (!bounds) { bounds = L.latLngBounds([[20.0, -5.0], [50.0, 45.0]]); }
    /* map.setView(bounds.getCenter(), Math.min(map.getBoundsZoom(bounds), 101), true); */
    map.fitBounds(bounds, {maxZoom: 10});
    pl_zoom({initialBounds: bounds}).addTo(map);
  }

  /* parse spatial info from JSON URI in the location page */
  $.getJSON($('link[rel="where"][type="application/json"]').attr('href'),
    function (where) {
      if (where && where.bbox) {
        bounds = L.latLngBounds([
          [where.bbox[1], where.bbox[0]],
          [where.bbox[3], where.bbox[2]] ]).pad(0.10);
      }
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
              };
          },
          onEachFeature: function (f, layer) {
            layer.bindPopup(
              '<dt><a href="' + f.properties.link + '">' + f.properties.title + '</a></dt>' + '<dd>' + f.properties.description + '</dd>'
            );
            if ($("h1").text() == f.properties.title) { target = layer; }
          }
        }).addTo(map);
      }
      if (bounds && baselineBounds) {
          bounds.extend(baselineBounds);
      }
      if (target !== null) {
        target.openPopup();
      }
      rebound();
    }
  );

  /* parse spatial info from JSON uri in the baseline location (if this is a working copy) */
  $.getJSON($('link[rel="baseline-where"][type="application/json"]').attr('href'),
    function (baselineWhere) {
      if (baselineWhere && baselineWhere.bbox) {
        baselineBounds = L.latLngBounds([
          [baselineWhere.bbox[1], baselineWhere.bbox[0]],
          [baselineWhere.bbox[3], baselineWhere.bbox[2]] ]).pad(0.10);
        if (bounds) {
          bounds.extend(baselineBounds);
        }
        else { bounds = baselineBounds; }
      }
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
              };
          },
          onEachFeature: function (f, layer) {
            layer.bindPopup(
              '<dt><a href="' + f.properties.link + '">' + f.properties.title + '</a></dt>' + '<dd>' + f.properties.description + '</dd>'
            );
          }
        }).addTo(map);
      }
      rebound();
    }
  );
});