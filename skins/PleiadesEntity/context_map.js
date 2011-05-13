/* context_map.js */

var MTID = 'aw';
var infoWindow = new google.maps.InfoWindow();
var map = null;
var where = null;
var overlays = [];
var r_neighbors = null;
var p_neighbors = null;

var placeIcon = new google.maps.MarkerImage(
    "http://google-maps-icons.googlecode.com/files/justice.png");

function getJSON(rel) {
  var documentNode = document;
  var linkNode = documentNode.evaluate(
      '//link[@rel="' + rel + '" and @type="application/json"]',
      documentNode,
      null,
      XPathResult.FIRST_ORDERED_NODE_TYPE,
      null).singleNodeValue;
  var uri = linkNode.getAttribute("href");
  var json = unescape(uri.split(',').pop());
  return jq.parseJSON(json);
}

function getKML(rel) {
  var documentNode = document;
  var linkNode = documentNode.evaluate(
      '//link[@rel="' + rel 
        + '" and @type="application/vnd.google-earth.kml+xml"]',
      documentNode,
      null,
      XPathResult.FIRST_ORDERED_NODE_TYPE,
      null).singleNodeValue;
  var uri = linkNode.getAttribute("href");
  return uri;
}

function getBounds(collection) {
  if (collection.hasOwnProperty('bbox') == true) {
    return collection.bbox;
  }
}

function clearContextOverlays() {
  if (overlays) {
    for (var i=0; i<overlays.length; i++) {
      overlays[i].setMap(null);
      }
    }
  }

function showContextOverlays() {
  if (overlays) {
    for (var i=0; i<overlays.length; i++) {
      overlays[i].setMap(map);
    }
  }
}

function deleteContextOverlays() {
  if (overlays) {
    for (var i=0; i<overlays.length; i++) {
      overlays[i].setMap(null);
    }
    overlays.length = 0;
  }
}

function popupNeighbor(evt) {
  /* Uses the global info window */
  var msg = document.createElement("div");
  msg.setAttribute("style", "overflow:auto");
  var head = document.createElement("h3");
  var tail = document.createElement("p");
  var details = document.createElement("a");
  details.setAttribute("href", evt.featureData.author.uri);
  jq(details).text("Details");
  jq(tail).append(details);
  jq(head).text(evt.featureData.name);
  jq(msg).append(head);
  jq(msg).append(unescape(unescape(evt.featureData.description)));
  jq(msg).append(tail);
  infoWindow.close();
  infoWindow.setOptions({position: evt.latLng, content: msg});
  infoWindow.open(map);
}

function popupContext(context) {
  /* Uses the global info window */
  var msg = document.createElement("div");
  msg.setAttribute("style", "overflow:auto");
  var head = document.createElement("h3");
  var tail = document.createElement("p");
  var details = document.createElement("a");
  details.setAttribute("href", context.link);
  jq(details).text("Details");
  jq(tail).append(details);
  jq(head).text(context.title);
  jq(msg).append(head);
  jq(msg).append(context.description);
  jq(msg).append(tail);
  infoWindow.close();
  infoWindow.setOptions({position: context.position, content: msg});
  infoWindow.open(map);
}

function registerContextClick(context, position, feature) {
  google.maps.event.addListener(
    context, 'click', function() {
      popupContext({
        position: position,
        title: feature.properties.title,
        link: feature.properties.link,
        description: feature.properties.description
        });
    });
}

function initialize() {

  where = getJSON('where');
  var bounds = getBounds(where);
  var latlng = new google.maps.LatLng(
    (bounds[1]+bounds[3])/2.0, (bounds[0]+bounds[2])/2.0);

  var myOptions = {
    zoom: 10,
    center: latlng,
    mapTypeId: google.maps.MapTypeId.TERRAIN
  };

  map = new google.maps.Map(
            document.getElementById("map"),
            myOptions);

  if ((bounds[2]-bounds[0])*(bounds[3]-bounds[1]) >= 0.001) {
    map.fitBounds(
      new google.maps.LatLngBounds(
        new google.maps.LatLng(bounds[1], bounds[0]), 
        new google.maps.LatLng(bounds[3], bounds[2])));
  }

  for (var i=0; i<where.features.length; i++) {

    var f = where.features[i];
    var geom = f.geometry;
      
    var relation = null;
    if (geom.hasOwnProperty('relation')) {
      relation = geom.relation;
    }

    var color = "#0000FF";
    var opacity = 1.0;
    if (relation != null) {
      opacity = 0.5;
    }

    if (f.geometry.type == 'Point') {
      var xy = new google.maps.LatLng(
                geom.coordinates[1], geom.coordinates[0]);
      var whereMark = new google.maps.Marker({
                position: xy, 
                icon: placeIcon,
                });
      overlays.push(whereMark);
      registerContextClick(whereMark, xy, f);
    }

    else if (f.geometry.type == 'Polygon') {
      var exterior = f.geometry.coordinates[0];
      var ring = [];
      var cx = 0.0;
      var cy = 0.0;
      var v = null;
      for (var j=0; j<exterior.length; j++) {
        v = exterior[j];
        ring.push(new google.maps.LatLng(v[1], v[0]));
        cx += v[0];
        cy += v[1];
      }
      cx = cx/exterior.length;
      cy = cy/exterior.length;
      var polygon = new google.maps.Polygon({
        paths: ring,
        strokeColor: color,
        strokeOpacity: opacity,
        strokeWeight: 3,
        strokeColor: color,
        fillOpacity: opacity/2.0
        });
      overlays.push(polygon);
      registerContextClick(polygon, new google.maps.LatLng(cy, cx), f);
    }
  }

  r_kml = getKML("nofollow alternate r-neighbors");
  p_kml = getKML("nofollow alternate p-neighbors");

  if (r_kml.substring(0, 16) != "http://localhost") {
    
    r_neighbors = new google.maps.KmlLayer(
        r_kml, {preserveViewport: true, suppressInfoWindows: true});
    p_neighbors = new google.maps.KmlLayer(
        p_kml, {preserveViewport: true, suppressInfoWindows: true});

    google.maps.event.addListener(
      r_neighbors, 'click', function(evt) {
        popupNeighbor(evt);
      });

    google.maps.event.addListener(
      p_neighbors, 'click', function(evt) {
        popupNeighbor(evt);
      });

    google.maps.event.addListener(
      r_neighbors, 'metadata_changed', function() {
        p_neighbors.setMap(map);
      });

    google.maps.event.addListener(
      p_neighbors, 'metadata_changed', function() {
        showContextOverlays();
      });

    r_neighbors.setMap(map);
  }
  else {
    showContextOverlays();
  }

}

registerPloneFunction(initialize);
