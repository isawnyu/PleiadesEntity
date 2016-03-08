/* context_map.js */
var google;
var $ = jQuery;
var MTID = 'aw';
var infoWindow = new google.maps.InfoWindow();
var map = null;
var roughOverlays = [];
var roughFeatures = [];
var contextOverlays = [];
var p_neighbors = null;

var worldBounds = new google.maps.LatLngBounds(
  new google.maps.LatLng(-90.0, -180.0), new google.maps.LatLng(90.0, 180.0));

var placeIcon = new google.maps.MarkerImage(
    "http://atlantides.org/images/justice-blue.png");

var baselineIcon = new google.maps.MarkerImage(
    "http://atlantides.org/images/justice-blue-light.png");

var connectionIcon = new google.maps.MarkerImage(
    "http://atlantides.org/images/justice-green.png");

var cloudIcon = new google.maps.MarkerImage(
    "http://atlantides.org/images/cloud-marker.png",
    null,
    null,
    new google.maps.Point(34, 29)
    );

var cloudIconG = new google.maps.MarkerImage(
    "http://atlantides.org/images/cloud-marker-green.png",
    null,
    null,
    new google.maps.Point(34, 29)
    );

function getJSON(rel) {
  var documentNode = document;
  var linkNode = documentNode.evaluate(
      '//link[@rel="' + rel + '" and @type="application/json"]',
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

function getKML(rel) {
  var documentNode = document;
  var linkNode = documentNode.evaluate(
      '//link[@rel="' + rel + '" and @type="application/vnd.google-earth.kml+xml"]',
      documentNode,
      null,
      XPathResult.FIRST_ORDERED_NODE_TYPE,
      null).singleNodeValue;
  if (linkNode !== null) {
    var uri = linkNode.getAttribute("href");
    return uri;
  }
  else {
    return null;
  }
}

function getBounds(collection) {
  if (!collection) { return null; }
  if (collection.hasOwnProperty('bbox') === true) {
    return collection.bbox;
  }
  else {
    return null;
  }
}

function addBounds(b1, b2) {
  if (!b2) { return b1; }
  else if (!b1) { return b2; }
  else {
    return [
      Math.min(b1[0], b2[0]), 
      Math.min(b1[1], b2[1]), 
      Math.max(b1[2], b2[2]), 
      Math.max(b1[3], b2[3])] ;
  }
}

function clearContextOverlays() {
  if (contextOverlays) {
    for (var i=0; i<contextOverlays.length; i++) {
      contextOverlays[i].setMap(null);
      }
    }
  }

function showContextOverlays() {
  if (contextOverlays) {
    for (var i=0; i<contextOverlays.length; i++) {
      contextOverlays[i].setMap(map);
    }
  }
}

function deleteContextOverlays() {
  if (contextOverlays) {
    for (var i=0; i<contextOverlays.length; i++) {
      contextOverlays[i].setMap(null);
    }
    contextOverlays.length = 0;
  }
}

function showRoughOverlays() {
  if (roughOverlays) {
    for (var i=0; i<roughOverlays.length; i++) {
      roughOverlays[i].setMap(map);
    }
  }
}

function popupKMLNeighbor(evt) {
  /* Uses the global info window */
  var msg = document.createElement("div");
  msg.setAttribute("style", "overflow:auto");
  var head = document.createElement("h2");
  var descr = document.createElement("p");
  var link = document.createElement("a");
  link.setAttribute("href", evt.featureData.author.uri);
  $(link).text(evt.featureData.snippet);
  $(head).text(evt.featureData.name);
  $(descr).html(unescape(unescape(evt.featureData.description)));
  $(msg).append(head);
  $(msg).append(link);
  $(msg).append(descr);
  infoWindow.close();
  infoWindow.setOptions({position: evt.latLng, content: msg});
  infoWindow.open(map);
}

function popupContext(context) {
  /* Uses the global info window */
  var msg = document.createElement("div");
  msg.setAttribute("style", "overflow:auto");
  var head = document.createElement("h2");
  var descr = document.createElement("p");
  var link = document.createElement("a");
  link.setAttribute("href", context.link);
  $(link).text(context.snippet);
  $(head).text(context.title);
  $(descr).html(unescape(unescape(context.description)));
  $(msg).append(head);
  $(msg).append(link);
  $(msg).append(descr);
  infoWindow.close();
  infoWindow.setOptions({position: context.position, content: msg});
  infoWindow.open(map);
}

function registerFeatureClick(marker, xy, properties, fid) {
  google.maps.event.addListener(
    marker, 'click', function(e) {
      popupContext({
        position: xy,
        id: fid,
        title: properties.title,
        link: properties.link,
        description: properties.description,
        snippet: properties.snippet
      });
    });
}

function registerMarkerClick(marker, properties, fid) {
  google.maps.event.addListener(
    marker, 'click', function(e) {
      popupContext({
        id: fid,
        position: marker.getPosition(),
        title: properties.title,
        link: properties.link,
        description: properties.description,
        snippet: properties.snippet
      });
    });
}

function registerCloudMouseover(marker, box) {
  google.maps.event.addListener(
    marker, 'mouseover', function(e) {
      box.setMap(map);
    });
}

function registerCloudMouseout(marker, box) {
  google.maps.event.addListener(
    marker, 'mouseout', function(e) {
      box.setMap(null);
    });
}

function cloudPosition(feature, mapBounds) {
  // Cloud's anchor point approaches context origin as we zoom in,
  // approaches other end of the line as we zoom out
  var coords = feature.geometry.coordinates;
  var bbox = feature.bbox;
  var mapLL = mapBounds.getSouthWest();
  var mapUR = mapBounds.getNorthEast();
  var mapDiameter = Math.sqrt(
    (mapUR.lat() - mapLL.lat())*(mapUR.lat() - mapLL.lat()) +
    (mapUR.lng() - mapLL.lng())*(mapUR.lng() - mapLL.lng()));
  var diameter = Math.sqrt(
    (bbox[2]-bbox[0])*(bbox[2]-bbox[0]) +
    (bbox[3]-bbox[1])*(bbox[3]-bbox[1]));
  var scale = mapDiameter/diameter;
  var c = 0.8;
  var f = c*scale/2.0;
  f = Math.min(1.0, f);
  var cloudLat = (1.0-f)*coords[0][1] + f*coords[1][1];
  var cloudLon = (1.0-f)*coords[0][0] + f*coords[1][0];
  return new google.maps.LatLng(cloudLat, cloudLon);
}

function make_overlays(collection, color, opacity, icon, zIndex) {
  var coords, cx, cy, j, xy, v, whereMark, exterior, ring;
  if (!collection || !collection.features) { return; }
  for (var i=0; i<collection.features.length; i++) {
    var f = collection.features[i];
    if (!f) {
      continue;
    }
    var geom = f.geometry;
    if (geom === null) {
      continue;
    }
    var relation = null;
    if (geom.hasOwnProperty('relation')) {
      relation = geom.relation;
    }
    if (relation !== null) {
      opacity *= 0.5;
    }
    if (f.type == "Feature") {
      if (f.geometry.type == 'Point') {
        xy = new google.maps.LatLng(
                  geom.coordinates[1], geom.coordinates[0]);
        whereMark = new google.maps.Marker({
                  position: xy, 
                  icon: icon,
                  zIndex: zIndex
                  });
        registerMarkerClick(whereMark, f.properties, f.id);
        contextOverlays.push(whereMark);
      }
      else if (geom.type == 'LineString') {
        coords = [];
        cx = 0.0;
        cy = 0.0;
        v = null;
        for (j=0; j<geom.coordinates.length; j++) {
          v = geom.coordinates[j];
          coords.push(new google.maps.LatLng(v[1], v[0]));
          cx += v[0];
          cy += v[1];
        }
        cx = cx/coords.length;
        cy = cy/coords.length;
        xy = new google.maps.LatLng(cy, cx);
        var polyline = new google.maps.Polyline({
          path: coords,
          strokeColor: color,
          strokeOpacity: opacity,
          strokeWeight: 3,
          zIndex: zIndex
          });
        registerFeatureClick(
            polyline, 
            new google.maps.LatLng(cy, cx), 
            f.properties,
            f.id);
        contextOverlays.push(polyline);
      }
      else if (f.geometry.type == 'Polygon') {
        exterior = f.geometry.coordinates[0];
        ring = [];
        cx = 0.0;
        cy = 0.0;
        v = null;
        for (j=0; j<exterior.length; j++) {
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
          fillOpacity: opacity/2.0,
          zIndex: zIndex
          });
        registerFeatureClick(
            polygon, 
            new google.maps.LatLng(cy, cx), 
            f.properties,
            f.id);
        contextOverlays.push(polygon);
      }
    }
    else if (f.type == "pleiades.stoa.org.BoxBoundedRoughFeature") {
      var cloudMark = new google.maps.Marker({
                position: null,
                icon: cloudIconG,
                zIndex: 100,
                });
      var cloudBox = new google.maps.Rectangle({
          bounds: new google.maps.LatLngBounds(
            new google.maps.LatLng(f.bbox[1], f.bbox[0]),
            new google.maps.LatLng(f.bbox[3], f.bbox[2])),
          strokeColor: color,
          strokeOpacity: opacity,
          strokeWeight: 3,
          fillOpacity: opacity/2.0
          });
      registerMarkerClick(cloudMark, f.properties, f.id);
      registerCloudMouseover(cloudMark, cloudBox);
      registerCloudMouseout(cloudMark, cloudBox);
      roughOverlays.push(cloudMark);
      roughFeatures.push(f);
    }
  }
  showRoughOverlays();
  showContextOverlays();
}

function initialize() {
  /*
   * 1. Get the KML of precisely located neighbors, register mouse listeners
   * 2. Populate a global array of roughly located neighbor aggregations, 
   *    with mouse listeners
   * 3. Populate a global array of context features, with mouse listeners
   * 4. Render map (Precise, rough, context)
   * 5. Register bounds change listener that redraws rough markers
   */
  var bounds, connectionBounds, baselineBounds;
  var mapOptions = {
    mapTypeId: google.maps.MapTypeId.TERRAIN
  };

  map = new google.maps.Map(
          document.getElementById("map"),
          mapOptions);

  var p_kml = getKML("nofollow alternate p-neighbors");
  if (p_kml !== null && p_kml.substring(0, 16) != "http://localhost") {
    p_neighbors = new google.maps.KmlLayer(
        p_kml, {preserveViewport: true, suppressInfoWindows: true});
    google.maps.event.addListener(
      p_neighbors, 'click', function(evt) {
        popupKMLNeighbor(evt);
      });
    google.maps.event.addListener(
      p_neighbors, 'metadata_changed', function() {
        var pBounds = p_neighbors.getDefaultViewport();
        if (
          pBounds !== null && 
          !pBounds.equals(worldBounds) &&
          map.getBounds() !== null) {
          map.fitBounds(pBounds.union(map.getBounds()));
        }
      });
  }

  function rebound() {
    /* Compute bounds of map from the several feature collections */
    /* bounds = addBounds(bounds, connectionBounds); */
    var combined_bounds = addBounds(bounds, baselineBounds);
    if (combined_bounds !== null) {
      map.fitBounds(
        new google.maps.LatLngBounds(
          new google.maps.LatLng(combined_bounds[1], combined_bounds[0]),
          new google.maps.LatLng(combined_bounds[3], combined_bounds[2])));
    }
  }

  $.getJSON($('link[rel="r-where"][type="application/json"]').attr('href'),
    function (rWhere) {
      for (var i=0; i<Math.min(rWhere.features.length, 10); i++) {
        var f = rWhere.features[i];
        var geom = f.geometry;
        if (geom === null) {
          continue;
        }
        if (f.type == "pleiades.stoa.org.BoxBoundedRoughFeature") {
          var cloudMark = new google.maps.Marker({
                    position: null, 
                    icon: cloudIcon,
                    zIndex: 100,
                    });
          var cloudBox = new google.maps.Rectangle({
              bounds: new google.maps.LatLngBounds(
                new google.maps.LatLng(f.bbox[1], f.bbox[0]),
                new google.maps.LatLng(f.bbox[3], f.bbox[2])),
              strokeColor: "#cc6633",
              strokeOpacity: 0.5,
              strokeWeight: 2,
              fillOpacity: 0.25
              });
          registerMarkerClick(cloudMark, f.properties, f.id);
          registerCloudMouseover(cloudMark, cloudBox);
          registerCloudMouseout(cloudMark, cloudBox);
          roughOverlays.push(cloudMark);
          roughFeatures.push(f);
        }
      }
      showRoughOverlays();
    }
  );

  $.getJSON($('link[rel="connections"][type="application/json"]').attr('href'),
    function (connections) {
      make_overlays(connections, "#00FF00", 0.5, connectionIcon, 101);
      connectionBounds = getBounds(connections);
    }
  );

  $.getJSON($('link[rel="baseline-where"][type="application/json"]').attr('href'),
    function (baselineWhere) {
      make_overlays(baselineWhere, "#00FF00", 0.5, baselineIcon, 102);
      baselineBounds = getBounds(baselineWhere);
      rebound();
    }
  );

  $.getJSON($('link[rel="where"][type="application/json"]').attr('href'),
    function (where) {
      make_overlays(where, "#0000FF", 1.0, placeIcon, 103);
      bounds = getBounds(where);
      rebound();
    }
  );

  google.maps.event.addListener(
    map, 'bounds_changed', function() {
      var mapBounds = map.getBounds();
      for (var i=0; i<roughOverlays.length; i++) {
        var marker = roughOverlays[i];
        marker.setMap(null);
        marker.setPosition(cloudPosition(roughFeatures[i], mapBounds));
        marker.setMap(map);
      }
    });
  
  /* Default view */
  var latlng = new google.maps.LatLng(35.0, 20.0);
  var zoom = 4;

  map.setCenter(latlng);
  map.setZoom(zoom);

  /*
  if (p_neighbors != null) {
    p_neighbors.setMap(map);
  }
  */
}

function overlayIndexOf(where, elem_id) {
  if (!where) { return -1; }
  for (var i=0;i<contextOverlays.length;i++) {
    var f = where.features[i];
    if (f.id == elem_id) {
      return i;
    }
  }
  return -1;
}

function raiseInMap() {
  var s = this.id.split("_");
  var where_name = s[1] || 'where';

  $.getJSON($('link[rel="' + where_name + '"][type="application/json"]').attr('href'),
    function (where) {
      var cx, cy, v, coords, exterior, j;
      var i = overlayIndexOf(where, s[0]);
      if (i < 0) { return; }
      var f = where.features[i];
      var properties = f.properties;
      var geom = f.geometry;
      var xy = null;
      if (geom.type == 'Point') {
        xy = new google.maps.LatLng(geom.coordinates[1], geom.coordinates[0]);
      }
      else if (geom.type == 'LineString') {
        coords = geom.coordinates;
        cx = 0.0;
        cy = 0.0;
        v = null;
        for (j=0; j<coords.length; j++) {
          v = coords[j];
          cx += v[0];
          cy += v[1];
        }
        cx = cx/coords.length;
        cy = cy/coords.length;
        xy = new google.maps.LatLng(cy, cx);
      }
      else if (geom.type == 'Polygon') {
        exterior = geom.coordinates[0];
        cx = 0.0;
        cy = 0.0;
        v = null;
        for (j=0; j<exterior.length; j++) {
          v = exterior[j];
          cx += v[0];
          cy += v[1];
        }
        cx = cx/exterior.length;
        cy = cy/exterior.length;
        xy = new google.maps.LatLng(cy, cx);
      }
      popupContext({
        position: xy,
        id: f.id,
        title: properties.title,
        link: properties.link,
        description: properties.description,
        snippet: properties.snippet
      });
    }
  );
}

registerPloneFunction(initialize);
