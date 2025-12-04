var $ = jQuery;
const boxpad = 50;
const max_zoom = 17;
const initial_zoom = 15;
// Bounds values
const INITIAL_WEST = -20.0;
const INITIAL_NORTH = 30.0;
const INITIAL_EAST = 85.0;
const INITIAL_SOUTH = 0.0;
const MAX_WEST = -30.0;
const MAX_NORTH = 80.0;
const MAX_EAST = 180.0;
const MAX_SOUTH = -45.0;

/* Configure and initialize map and standard controls */
mapboxgl.accessToken = 'pk.eyJ1IjoiaXNhd255dSIsImEiOiJjbWluMzA2YWgyNHY1M2dweHRneGQwemVjIn0.2OjZgOxVAh8qNpY5rDipGg';
mapboxgl.setRTLTextPlugin(
    'https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-rtl-text/v0.2.3/mapbox-gl-rtl-text.js',
    null,
    true // Lazy load the plugin
);

// Bounding boxes are defined by SW and NE corners
const max_bounds = new mapboxgl.LngLatBounds([
    [MAX_WEST, MAX_SOUTH],
    [MAX_EAST, MAX_NORTH]
]);
var bounds = new mapboxgl.LngLatBounds([
    [INITIAL_WEST, INITIAL_SOUTH],
    [INITIAL_EAST, INITIAL_NORTH]
]);
var mapOptionsInit = {
    attributionControl: true,
    customAttribution: [
        'Base style derived from Mapbox Satellite Streets.',
        'Pleiades layers and interaction design by Sean Gillies, David Glick, Alec Mitchell, Ryan M. Horne, and Tom Elliott.'
    ],
    container: 'map',
    style: 'mapbox://styles/isawnyu/ckg9eqejk2j4a19oexu5ywrqu',
    maxBounds: max_bounds,
    bounds: bounds,
    renderWorldCopies: false,
    maxZoom: max_zoom,
};
var map = new mapboxgl.Map(mapOptionsInit);
map = map.addControl(new mapboxgl.NavigationControl({
    showCompass: false,
}), 'top-left');
map = map.addControl(new mapboxgl.ScaleControl());
map.scrollZoom.disable();

/* Define and initialize custom controls */
/* Original class implementation by Kristjan Tallinn via https://codepen.io/kriz/pen/jdxYXY */

class MapboxGLButtonControl {
    constructor({
        className = "",
        title = "",
        eventHandler = mapboxgl.eventHandler,
        container = undefined
    }) {
        this._className = className;
        this._title = title;
        this._eventHandler = eventHandler;
        this._container = container;
    }
    onAdd(map) {
        this._btn = document.createElement("button");
        this._btn.className = "mapboxgl-ctrl-icon" + " " + this._className;
        this._btn.type = "button";
        this._btn.title = this._title;
        this._btn.onclick = this._eventHandler;

        this._wrapper = document.createElement("span");
        this._wrapper.className = "mapboxgl-ctrl-icon";
        this._wrapper.setAttribute('aria-hidden', true);
        this._wrapper.appendChild(this._btn);

        if (this._container === undefined) {
            this._container = document.createElement("div");
            this._container.className = "mapboxgl-ctrl-group mapboxgl-ctrl";
        } else {
            this._container = document.getElementById(this._containerID);
        }
        this._container.appendChild(this._wrapper);

        return this._container;
    }
    onRemove() {
        this._container.parentNode.removeChild(this._container);
        this._map = undefined;
    }
}
// Controls to reset zoom & pan

function hdlResetBox() {
    map.fitBounds(bounds, { 'padding': boxpad });
}
map = map.addControl(new MapboxGLButtonControl({
    className: "mapbox-gl-reset-box",
    title: "Reset Map View",
    eventHandler: hdlResetBox
}), 'top-left');

/* Define styles and layouts for the layers we will use */
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
        }
    },
    'location-geometries': {
        'type': 'line',
        'layout': {},
        'paint': {
            'line-width': 3,
            'line-color': '#5587fc'
        }
    },
    'location-buffers': {
        'type': 'fill',
        'layout': {'visibility': 'none'},
        'paint': {
            'fill-outline-color': 'rgba(255, 255, 0, 1)',
            'fill-antialias': true,
            'fill-color': 'rgba(255, 255, 0, 0.3)'
        }
    },
    'connections-inbound': {
        'type': 'symbol',
        'layout': {
            'icon-image': 'interest-green-15-halo',
            'icon-allow-overlap': true
        },
        'filter': ['==', 'inbound', ['get', 'direction']]
    }
}
if (map.loaded()) {
    populateMap(map);
} else {
    map.on('load', () => populateMap(map));
}
map.on('click', function(e) {
    var features = map.queryRenderedFeatures(
        e.point, {
            layers: [
                'layer-representative-point',
                'layer-location-points',
                'layer-connections-inbound',
                'layer-location-polygons',
                'layer-location-geometries',
                'layer-location-buffers'
            ]
        });
    if (features.length > 0) {
        var feature = features[0];
        var snippet;
        if (feature.properties.link !== undefined) {
            snippet = '<dd><a href="' + feature.properties.link + '">' + feature.properties.title + '</a></dd>'
        } else {
            snippet = '<dd>' + feature.properties.title + '</dd>'
        }
        if (feature.properties.description !== undefined) {
            var desc;
            var words = feature.properties.description.split(' ');
            if (words.length > 25) {
                desc = words.slice(0, 26).join(' ') + '...'
            } else {
                desc = feature.properties.description;
            }
            snippet += '<dt>' + desc + '</dt>'
        }
        new mapboxgl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(snippet)
            .addTo(map);
    }
});

$('input#accuracy-buffer').on('change', function (){
    if ($(this).is(':checked')) {
        map.setLayoutProperty('layer-location-buffers', 'visibility', 'visible');
    } else {
        map.setLayoutProperty('layer-location-buffers', 'visibility', 'none');
    }
})

function populateMap(map) {

    var jurl = $('link[rel="where"][').attr('href');
    var rdata = {};
    if ($('body').attr('class').includes('userrole-authenticated')) {
        rdata = { _: new Date().getTime() };
    }
    $.getJSON(jurl, rdata, function(j) {
        var sw, ne, features;
        bounds = new mapboxgl.LngLatBounds();
        // Set an initial zoom level/boundary based on JSON
        if (j.bbox !== null) {
            sw = new mapboxgl.LngLat(j.bbox[0], j.bbox[1]);
            ne = new mapboxgl.LngLat(j.bbox[2], j.bbox[3]);
            bounds.extend(sw);
            bounds.extend(ne);
            map.fitBounds(bounds, { 'padding': boxpad, 'maxZoom': initial_zoom });
        }
        plotReprPoint(map, j);
        map.flyTo({ 'center': j.reprPoint });
        features = plotLocations(map, j);
        var extend_coords = function (coords_structure) {
            if (!coords_structure.length) {
                return;
            }
            if (Number.isFinite(coords_structure[0])) {
                bounds.extend(coords_structure);
            } else {
                coords_structure.forEach(extend_coords);
            }
        }
        features.forEach(function (feature) {
            if (!feature.geometry || !feature.geometry.coordinates) {
                return;
            }
            extend_coords(feature.geometry.coordinates);
        });
        // // Re-zoom
        if (features.length && bounds.getNorthEast()) {
            map.fitBounds(bounds, { 'padding': boxpad, 'maxZoom': initial_zoom });
        }
        plotConnections(map, j);
    });
}

function makeLayer(map, layerTitle, features, before = undefined) {
    var sourceID = layerTitle.toLowerCase().replace('(', '').replace(')', '').replace(' ', '-');
    if (!layerMetadata[sourceID]) {
        return;
    }
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
        'source': sourceID
            // 'maxzoom': maxzoom_awmc // over-zoom as necessary
    };
    Object.keys(layerMetadata[sourceID]).forEach(k => options[k] = layerMetadata[sourceID][k]);
    if (typeof(before) === "undefined") {
        map.addLayer(options);
    } else {
        map.addLayer(options, before);
    }
    map.on('mouseenter', layerID, function() {
        map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', layerID, function() {
        map.getCanvas().style.cursor = '';
    });
    restack(map);
}

function plotConnections(map, j) {
    let outbound = j.connections.map(a => a.connectsTo);
    var coords;
    var jurl = $('link[rel="connections"][type="application/json"]').attr('href');
    var rdata = {};
    if ($('body').attr('class').includes('userrole-authenticated')) {
        rdata = { _: new Date().getTime() };
    }
    $.getJSON(jurl, rdata,
        function(cnxj) {
            cnxj.features.forEach(function(connection) {
                var predicate = connection.properties.link;
                if (outbound.indexOf(predicate) != -1) {
                    connection.properties['direction'] = 'outbound';
                } else {
                    connection.properties['direction'] = 'inbound';
                    coords = connection.geometry.coordinates;
                    if (!bounds.contains(coords)) {
                        var here = new mapboxgl.LngLat(coords[0], coords[1]);
                        bounds.extend(here);
                    }
                }
            });
            makeLayer(map, 'Connections Inbound', cnxj.features);
            map.fitBounds(bounds, { 'padding': boxpad });
        });
}

function plotLocations(map, j) {
    var pointFeatures = Array();
    var polyFeatures = Array();
    var otherFeatures = Array();
    var locationBuffers = Array();
    j.locations.forEach(function(location) {
        var geoType = location.geometry.type;
        var feature = {
            'type': 'Feature',
            'geometry': location.geometry,
            'properties': {
                'title': location.title,
                'description': location.description,
                'link': location.uri
            }
        }
        if (geoType == 'Point') {
            pointFeatures.push(feature);
        } else if (geoType == 'Polygon') {
            polyFeatures.push(feature);
        } else {
            otherFeatures.push(feature);
        }
        if (location.accuracy_value) {
            var buffer = turf.convex.default(turf.buffer({
                'type': 'Feature',
                'geometry': location.geometry
            }, location.accuracy_value, {units: 'meters'}));
            buffer.properties = {
                'title': 'Accuracy buffer for ' + location.title,
                'description': location.accuracy_value.toString() + ' meter accuracy buffer'
            }
            locationBuffers.push(buffer);
        }
    });
    makeLayer(map, 'Location Polygons', polyFeatures);
    makeLayer(map, 'Location Points', pointFeatures);
    makeLayer(map, 'Location Geometries', otherFeatures);
    makeLayer(map, 'Location Buffers', locationBuffers);
    if (locationBuffers.length <= 0) {
        $('input#accuracy-buffer').prop('disabled', true);
        $('input#accuracy-buffer + label').text('No location accuracy information available');
    }
    return pointFeatures.concat(polyFeatures).concat(otherFeatures).concat(locationBuffers);
}

function plotReprPoint(map, j) {
    var features = [{
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': j.reprPoint
        },
        'properties': {
            'title': 'Representative point for ' + j.title,
            'icon': 'repr-point',
            'link': undefined
        }
    }]
    makeLayer(map, 'Representative Point', features);
}

function restack(map) {
    const desired_layer_order = ['background-sepia', 'satellite-sepia', 'admin-1-boundary-bg', 'admin-0-boundary-bg', 'admin-1-boundary', 'admin-0-boundary', 'admin-0-boundary-disputed', 'settlement-subdivision-label', 'settlement-minor-label', 'settlement-major-label', 'state-label', 'country-label', 'layer-location-buffers', 'layer-location-polygons', 'layer-location-geometries', 'layer-connections-inbound', 'layer-location-points', 'layer-representative-point'];
    var i;
    var this_layer;
    var current_layer_order;
    var current_layers = map.getStyle().layers;
    for (i = current_layers.length - 1; i > 2; i--) {
        current_layer_order = current_layers.map(({ id }) => id);
        this_layer = current_layer_order[i];
        while (current_layer_order.indexOf(this_layer) > desired_layer_order.indexOf(this_layer)) {
            map.moveLayer(this_layer, current_layer_order[current_layer_order.indexOf(this_layer) - 1]);
            current_layers = map.getStyle().layers;
            current_layer_order = current_layers.map(({ id }) => id);
        }
    }
}