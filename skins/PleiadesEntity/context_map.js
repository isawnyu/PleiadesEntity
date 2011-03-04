  var MTID = 'aw';
  var infowindow = new google.maps.InfoWindow();
  var map = null;
  var where = null;
  var overlays = [];
  var r_neighbors = null;
  var p_neighbors = null;

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

    map = new google.maps.Map(document.getElementById("map"),
        myOptions);

    if ((bounds[2]-bounds[0])*(bounds[3]-bounds[1]) >= 0.001) {
      map.fitBounds(
        new google.maps.LatLngBounds(
          new google.maps.LatLng(bounds[1], bounds[0]), 
          new google.maps.LatLng(bounds[3], bounds[2])));
    }

    /*
    r_neighbors = new google.maps.KmlLayer(
      getKML("alternate r-neighbors"), {preserveViewport: true});
    */
    p_neighbors = new google.maps.KmlLayer(
      getKML("alternate p-neighbors"), {preserveViewport: true});

    var nfeatures = where.features.length;
    for (var i=0; i<nfeatures; i++) {
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
        overlays.push(new google.maps.Marker({position: xy}));
      }

      else if (f.geometry.type == 'Polygon') {
        var exterior = f.geometry.coordinates[0];
        var ring = [];
        for (var j=0; j<exterior.length; j++) {
          ring.push(new google.maps.LatLng(exterior[j][1], exterior[j][0]));
        }
        var polygon = new google.maps.Polygon({
          paths: ring,
          strokeColor: color,
          strokeOpacity: opacity,
          strokeWeight: 3,
          strokeColor: color,
          fillOpacity: opacity/2.0
          });
        overlays.push(polygon);
      }
    }

    /*
    google.maps.event.addListener(
      r_neighbors, 'metadata_changed', function() {
        p_neighbors.setMap(map);
      });
    */

    google.maps.event.addListener(
      p_neighbors, 'metadata_changed', function() {
        showContextOverlays();
      });

    p_neighbors.setMap(map);
  }

  registerPloneFunction(initialize);


