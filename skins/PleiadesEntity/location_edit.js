
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

/* Shows the location data using the given layer */
function showLocation(layer, data, bounds) {
  if (layer) { 
    map.removeLayer(layer);
  }
  layer = L.GeoJSON.geometryToLayer(data);
  layer.bindPopup(data.description);
  layer.addTo(map);
  layer.openPopup();
  if (bounds) { map.fitBounds(bounds); }
}

/* On change of the geometry form field, update the editing layer and map. */
jq("textarea#geometry").change(function() {
  var geom_val = jq("textarea#geometry").val().trim();
  var json = toGeoJSON(geom_val);
  jq("textarea#geometry").val(geom_val);
  var f = { type: 'Feature', id: 'editing', 
    description: 'Location currently being edited',
    geometry: jq.parseJSON(json) };
  editing = L.GeoJSON.geometryToLayer(f);

  /* Test intersection with the parent object, showing a message in the
   * popup if the location is an outlier. */
  var test = false;
  var new_bounds = null;
  try {
    test = L.latLngBounds(bounds).intersects(editing.getBounds());
    new_bounds = L.latLngBounds(bounds).extend(editing.getBounds());
  }
  catch(err) {
    test = L.latLngBounds(bounds).contains(editing.getLatLng());
    new_bounds = L.latLngBounds(bounds).extend(editing.getLatLng());
  }
  if (!test) {
    f.description = "This location is an outlier... is it correct?";
  }
  showLocation(editing, f, new_bounds.pad(0.1));
});

/* Initialize the location edit map based on current or suggested coords. */
var geom_val = jq("textarea#geometry").val().trim();

if (!geom_val || geom_val == "{}" && bounds) {
  var center = L.latLngBounds(bounds).getCenter();
  jq("textarea#geometry").val(center.lat + ", " + center.lng);
  showLocation(editing, {type: 'Feature', id: 'editing', 
      description: 'Suggested location, please change in the form field',
      geometry: {type: "Point", coordinates: [center.lng, center.lat]} } );
}
else if (geom_val && geom_val != "{}") {
  json = toGeoJSON(geom_val);
  jq("textarea#geometry").val(json);
  showLocation(editing, {type: 'Feature', id: 'editing', 
     description: 'Location currently being edited',
     geometry: jq.parseJSON(json) } );
}

