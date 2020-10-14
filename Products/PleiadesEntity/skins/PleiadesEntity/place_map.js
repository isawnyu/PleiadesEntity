var $ = jQuery;
const boxpad = 50;
const max_zoom = 17;
const initial_zoom = 15;

/* Configure and initialize map and standard controls */
mapboxgl.accessToken = 'pk.eyJ1IjoiaXNhd255dSIsImEiOiJja2FlaWk4MG0yaHY0MnNvemRneWF0d2RnIn0.FgwFQtymPTHYPYYha5mfHw';
mapboxgl.setRTLTextPlugin(
    'https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-rtl-text/v0.2.3/mapbox-gl-rtl-text.js',
    null,
    true // Lazy load the plugin
);
var max_bounds = new mapboxgl.LngLatBounds([
    [-45, -20],
    [160, 80]
]);
var bounds = new mapboxgl.LngLatBounds([
    [-20, 0],
    [85, 30]
])
var mapOptionsInit = {
    attributionControl: false,
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
    'connections-inbound': {
        'type': 'symbol',
        'layout': {
            'icon-image': 'interest-green-15',
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
                'layer-location-polygons'
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

function populateMap(map) {
    var jurl = $('link[rel="canonical"]').attr('href') + '/json'
    $.getJSON(jurl, function(j) {
        var sw = new mapboxgl.LngLat(j.bbox[0], j.bbox[1]);
        var ne = new mapboxgl.LngLat(j.bbox[2], j.bbox[3]);
        bounds = new mapboxgl.LngLatBounds(sw, ne);
        plotReprPoint(map, j);
        map.flyTo({ 'center': j.reprPoint });
        map.fitBounds(bounds, { 'padding': boxpad, 'maxZoom': initial_zoom });
        plotLocations(map, j);
        plotConnections(map, j);
    });
}

function makeLayer(map, layerTitle, features, before = undefined) {
    var sourceID = layerTitle.toLowerCase().replace('(', '').replace(')', '').replace(' ', '-');
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
    if (typeof(before) === undefined) {
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
    $.getJSON($('link[rel="connections"][type="application/json"]').attr('href'),
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
                        map.fitBounds(bounds, { 'padding': boxpad });
                    }
                }
            });
            makeLayer(map, 'Connections Inbound', cnxj.features);
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
                'description': location.description,
                'link': location.uri
            }
        }
        if (geoType == 'Point') {
            pointFeatures.push(feature);
        } else if (geoType == 'Polygon') {
            polyFeatures.push(feature);
        } else {
            console.error('Unsupported feature geometry', geoType);
        }
    });
    makeLayer(map, 'Location Polygons', polyFeatures);
    makeLayer(map, 'Location Points', pointFeatures);
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
    const desired_layer_order = ['background-sepia', 'satellite-sepia', 'admin-1-boundary-bg', 'admin-0-boundary-bg', 'admin-1-boundary', 'admin-0-boundary', 'admin-0-boundary-disputed', 'settlement-subdivision-label', 'settlement-minor-label', 'settlement-major-label', 'state-label', 'country-label', 'layer-location-polygons', 'layer-connections-inbound', 'layer-location-points', 'layer-representative-point'];
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