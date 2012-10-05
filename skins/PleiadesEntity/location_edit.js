
var editing = null;

function toGeoJSON(val) {
/* Given trimmed text that contains a lat/long, GeoJSON, or WKT representation
 * of a geometric object, normalize and convert to GeoJSON. */
  if (val.indexOf("{") != 0) {
    // Have we been given a latitude, longitude pair?
    var match = val.match(/^(\-?\d+(\.\d+)?)\s*,*\s*(\-?\d+(\.\d+)?)/);
    if (match) {
      return '{"type": "Point", "coordinates": [' 
        + match[3] + ',' + match[1] + ']}';
    }
    // TODO: WKT
    else { return "{}"; }
  }
  else { 
    var point_pat = /point/i;
    var line_pat = /linestring/i;
    var polygon_pat = /polygon/i;
    var mpoint_pat = /multipoint/i;
    var mline_pat = /multilinestring/i;
    var mpolygon_pat = /multipolygon/i;
    var type_pat = /type/i;
    var coords_pat = /coordinates/i;
    var json = val.replace(point_pat, "Point");
    json = json.replace(line_pat, "LineString");
    json = json.replace(polygon_pat, "Polygon");
    json = json.replace(mpoint_pat, "MultiPoint");
    json = json.replace(mline_pat, "MultiLineString");
    json = json.replace(mpolygon_pat, "MultiPolygon");
    json = json.replace(type_pat, "type");
    json = json.replace(coords_pat, "coordinates")
    return json;
  }
}

function precisionDecimalPlaces(map) {
  var llBounds = map.getBounds();
  var xyBounds = map.getPixelBounds();
  var dLat = (
    llBounds.getNorthEast().lat - llBounds.getSouthWest().lat)/(
    xyBounds.getBottomLeft().y - xyBounds.getTopRight().y);
  var dLon = (
    llBounds.getNorthEast().lng - llBounds.getSouthWest().lng)/(
    xyBounds.getTopRight().x - xyBounds.getBottomLeft().x);
  var degreesPerPixel = Math.max(dLat, dLon);
  return Math.floor(Math.abs(Math.log(degreesPerPixel)/Math.LN10));
}

function truncateCoords(value, map) {
  return value.toFixed(precisionDecimalPlaces(map));
}

var geom_field = jq("textarea#geometry");

function updateFieldFromDrag(e) {
  var coords = e.target.getLatLng();
  var geom_val = truncateCoords(coords.lat, map) + ", " + truncateCoords(coords.lng, map);
  geom_field.val(geom_val);
  var json = toGeoJSON(geom_val);
  var f = { type: 'Feature', id: 'editing', 
    description: 'Location currently being edited',
    geometry: jq.parseJSON(json) };
  
  var test_layer = L.GeoJSON.geometryToLayer(f);
  editing = showLocation(map, editing, f, null);
}

/* Shows the location data using the given layer */
function showLocation(map, layer, data, bounds) {
  if (layer && map.hasLayer(layer)) {
    layer.closePopup();
    map.removeLayer(layer);
  }
  var layer = L.GeoJSON.geometryToLayer(data);
  layer.bindPopup(data.description);
  layer.addTo(map);
  layer.openPopup();
  try {
    layer.dragging.enable();
  }
  catch(err) {
    // do nothing if it's a line, polygon, other non-marker object.
  }
  if (bounds) { 
    map.setView(
      bounds.getCenter(), 
      Math.min(map.getBoundsZoom(bounds), 11), 
      true );
 }
  
  /* On drag end, update the form field */
  layer.on('dragend', updateFieldFromDrag);
  return layer;
}

/* On change of the geometry form field, update the editing layer and map. */
jq("textarea#geometry").change(function() {
  var geom_val = jq("textarea#geometry").val().trim();
  var json = toGeoJSON(geom_val);
  jq("textarea#geometry").val(geom_val);
  var f = { type: 'Feature', id: 'editing', 
    description: 'Location currently being edited',
    geometry: jq.parseJSON(json) };
  
  var test_layer = L.GeoJSON.geometryToLayer(f);

  /* Test intersection with the parent object, showing a message in the
   * popup if the location is an outlier. */
  var test = false;
  var new_bounds = null;
  try {
    test = L.latLngBounds(bounds).intersects(test_layer.getBounds());
    new_bounds = L.latLngBounds(bounds).extend(test_layer.getBounds());
  }
  catch(err) {
    test = L.latLngBounds(bounds).contains(test_layer.getLatLng());
    new_bounds = L.latLngBounds(bounds).extend(test_layer.getLatLng());
  }
  if (!test) {
    f.description = "This location is an outlier... is it correct?";
  }
  editing = showLocation(map, editing, f, new_bounds.pad(0.1));
});

/* Initialize the location edit map based on current or suggested coords. */
var geom_val = jq("textarea#geometry").val().trim();

if (!geom_val || geom_val == "{}" && bounds) {
  var center = L.latLngBounds(bounds).getCenter();
  jq("textarea#geometry").val(truncateCoords(center.lat, map) + ", " + truncateCoords(center.lng, map));
  editing = showLocation(map, editing, {type: 'Feature', id: 'editing', 
      description: 'Suggested location, please change in the form field',
      geometry: {type: "Point", coordinates: [center.lng, center.lat]} } );
}
else if (geom_val && geom_val != "{}") {
  json = toGeoJSON(geom_val);
  jq("textarea#geometry").val(json);
  editing = showLocation(map, editing, {type: 'Feature', id: 'editing', 
     description: 'Location currently being edited',
     geometry: jq.parseJSON(json) } );
}

