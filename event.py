import geojson
import logging
import re
from os import makedirs

from Acquisition import aq_inner, aq_parent
from plone.app.iterate.interfaces import IAfterCheckinEvent
from Products.CMFCore.interfaces import IActionSucceededEvent, IContentish
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from DateTime import DateTime

from Products.PleiadesEntity.content.interfaces import ILocation, IName
from Products.PleiadesEntity.content.interfaces import IFeature, IPlace
from Products.PleiadesEntity.time import temporal_overlap
from pleiades.transliteration import transliterate_name
from pleiades.json.browser import getContents, wrap, W
from pleiades.geographer.geo import extent, representative_point
from shapely.geometry import asShape, LineString, mapping, Point, shape

log = logging.getLogger('PleiadesEntity')

pidrex = re.compile('^\d+$')

def reindexWhole(obj, event):
    for p in obj.getBRefs('hasPart'):
        log.debug("Reindexing whole %s", p)
        p.reindexObject()

def reindexContainer(obj, event):
    x = aq_inner(obj)
    f = aq_parent(x)
    if IPlace.providedBy(f):
        log.debug("Reindexing container %s", f)
        f.reindexObject()
        reindexWhole(f, event)
        writePlaceJSON(f, event)


def writePlaceJSON(place, event, published_only=True):
    wftool = getToolByName(place, "portal_workflow")
    status = wftool.getStatusOf("pleiades_entity_workflow", place)
    if published_only and status and status.get("review_state", None) != "published":
            return

    # determine the filename to write, and what directory to use, so the filesystem doesn't choke
    pid = place.getId()
    m = pidrex.match(pid)
    if not m:
        # don't write out json for temp places, e.g., copy_of_12345
        return
    pidbits = list(pid)
    pidpath = '/home/zope/pleiades/json/' + '/'.join(pidbits[:3]) + "/%s" % pid
    try:
        makedirs(pidpath)
    except OSError:
        pass

    fn = "%s/json" % pidpath

    # Create a JSON-LD Context object. 
    #See http://json-ld.org/spec/latest/json-ld.
    ctx = {
        'type': '@type',
        'id': '@id',
        'FeatureCollection': '_:n1',
        'bbox': 'http://geovocab.org/geometry#bbox',
        'features': '_:n3',
        'Feature': 'http://geovocab.org/spatial#Feature',
        'properties': '_:n4',
        'geometry': 'http://geovocab.org/geometry#geometry',
        'Point': 'http://geovocab.org/geometry#Point',
        'LineString': 'http://geovocab.org/geometry#LineString',
        'Polygon': 'http://geovocab.org/geometry#Polygon',
        'MultiPoint': 'http://geovocab.org/geometry#MultiPoint',
        'MultiLineString': 'http://geovocab.org/geometry#MultiLineString',
        'MultiPolygon': 'http://geovocab.org/geometry#MultiPolygon',
        'GeometryCollection': 
            'http://geovocab.org/geometry#GeometryCollection',
        'coordinates': '_:n5',
        'description': 'http://purl.org/dc/terms/description',
        'title': 'http://purl.org/dc/terms/title',
        'link': '_:n6',
        'location_precision': '_:n7',
        'snippet': 'http://purl.org/dc/terms/abstract',
        'connectsWith': '_:n8',
        'names': '_:n9',
        'recent_changes': '_:n10',
        'reprPoint': '_:n11'
        }


    # Locations that belong to this place
    xs = []
    ys = []
    location_objects = place.listFolderContents(contentFilter={'portal_type':'Location'})
    if len(location_objects) > 0:
        features = []
        for ob in location_objects:
            status = wftool.getStatusOf("pleiades_entity_workflow", ob)
            if status and status.get("review_state", None) == "published":
                features.append(wrap(ob))
    else:
        features = [wrap(ob) for ob in place.getFeatures()] \
                 + [wrap(ob) for ob in place.getParts()]

    # Geometry aspects of the place itself
    try:
        ex = extent(place)
    except:
        precision = "unlocated"
        bbox = None
    else:  
        try:  
            bbox = shape(ex['extent']).bounds
        except:
            bbox = None
        try:
            precision = ex['precision']
        except:
            precision = "unlocated"
    reprPoint = representative_point(place)['coords']


    # Names that belong to this place
    name_objects = place.listFolderContents(contentFilter={'portal_type':'Name'})
    names = []
    for ob in name_objects:
        status = wftool.getStatusOf("pleiades_entity_workflow", ob)
        if status and status.get("review_state", None) == "published":
            names.append(ob.getNameAttested() or ob.getNameTransliterated())

    # Connections to other places
    func = lambda f: wftool.getStatusOf("pleiades_entity_workflow", f).get("review_state", None) == 'published'
    connections = [ob.getId() for ob in list(
                place.getConnections() + place.getConnections_from())
                if func(ob) ]

    # Modification time, actor, contributors
    recent_changes = []
    records = []
    rtool = getToolByName(place, "portal_repository")    
    mtool = getToolByName(place, 'portal_membership')
    history = rtool.getHistoryMetadata(place)
    if history:
        metadata = history.retrieve(-1)['metadata']['sys_metadata']
        records.append((metadata['timestamp'], metadata))
    for ob in place.listFolderContents():
        history = rtool.getHistoryMetadata(ob)
        if not history: continue
        metadata = history.retrieve(-1)['metadata']['sys_metadata']
        records.append((metadata['timestamp'], metadata))
    records = sorted(records, reverse=True)
    for record in records:
        principal = record[1]['principal']
        modified = DateTime(record[0]).HTML4()
        member = mtool.getMemberById(principal)
        pname = member.getProperty("fullname")
        comment = record[1]['comment']
        recent_changes.append(
            dict(modified=modified, username=principal, fullname=[pname,principal][pname==''], comment=comment))

    # Build the dictionary that will be saved as JSON
    # @context (for json ld)
    # type == FeatureCollection
    # id
    # title
    # description 
    # features
    # names
    # reprPoint
    # bbox    
    # connectsWith
    # recent_changes

    d = {
        '@context': ctx,
        'type': 'FeatureCollection',
        'id': pid,
        'title': place.Title(),
        'description' : place.Description(),
        'features': sorted(features, key=W, reverse=True),
        'names': [unicode(n, "utf-8") for n in names],
        'reprPoint': reprPoint,
        'bbox': bbox,
        'precision': precision,
        'connectsWith': connections,
        'recent_changes': recent_changes
    }


    f = open(fn, 'w')
    f.write(geojson.dumps(d))
    f.close()



@adapter(IPlace, IObjectModifiedEvent)
def placeJSONSubscriber(obj, event):
    log.debug("Event handled: %s, %s", obj, event)
    writePlaceJSON(obj, event)

@adapter(IName, IObjectModifiedEvent)
def nameChangeSubscriber(obj, event):
    obj.getField('title').set(
        obj, obj.getNameTransliterated().split(',')[0].strip() or "Untitled")
    reindexContainer(obj, event)
    
@adapter(ILocation, IObjectModifiedEvent)
def locationChangeSubscriber(obj, event):
    log.debug("Event handled: %s, %s", obj, event)

    # Reindex co-temporal names of the parent place since they are being
    # localized by this location.
    place = aq_parent(aq_inner(obj))
    for o in filter(
            lambda x: temporal_overlap(obj, x),
            place.getNames() ):
        o.reindexObject()

    reindexContainer(obj, event)

@adapter(IFeature, IObjectModifiedEvent)
def featureChangeSubscriber(obj, event):
    reindexWhole(obj, event)

@adapter(IContentish, IObjectModifiedEvent)
def contributorsSubscriber(obj, event):
    # Ensure that principals from the obj's version history are represented
    # in the Contributors field.
    
    def fixSeanTom(p):
        if p in ("T. Elliott", "Tom Elliott"):
            return "thomase"
        elif p in ("S. Gillies", "Sean Gillies", "admin"):
            return "sgillies"
        else:
            return p

    def repairPrincipal(p):
        return [fixSeanTom(v.strip()) for v in p.split(",")]
    
    def repairPrincipals(seq):
        return reduce(lambda x, y: x+y, map(repairPrincipal, seq), [])

    creators = set(repairPrincipals(obj.Creators()))
    contributors = set(filter(
        lambda x: x not in creators, 
        repairPrincipals(obj.Contributors())))
    credited = creators.union(contributors)
    
    def getPrincipals(ob):
        principals = set()
        context = aq_inner(ob)
        rt = getToolByName(context, "portal_repository")
        history = rt.getHistoryMetadata(context)
        if history:
            for i in range(len(history)):
                metadata = history.retrieve(i)['metadata']['sys_metadata']
                for p in repairPrincipal(metadata['principal']):
                    principals.add(p)
        return principals

    try:
        principals = getPrincipals(obj)
        if IPlace.providedBy(obj):
            for sub in (obj.getNames() + obj.getLocations()):
                sub_principals = set(
                    repairPrincipals(sub.Creators()) \
                    + repairPrincipals(sub.Contributors()))
                principals = principals.union(sub_principals)
        uncredited = principals - credited
        
        obj.setCreators(list(creators))
        obj.setContributors(list(contributors.union(uncredited)))
        obj.reindexObject(idxs=['Creator', 'Contributors'])
        
        context = aq_inner(obj)
        parent = aq_parent(context)
        if IPlace.providedBy(parent):
            contributorsSubscriber(parent, event)

    except:
        log.exception(
            "Failed to sync Contributors with revision history" )

# We want to reindex containers when locations, names change state
#
@adapter(ILocation, IActionSucceededEvent)
def locationActionSucceededSubscriber(obj, event):
    log.debug("Event handled: %s, %s", obj, event)
    reindexContainer(obj, event)

@adapter(IName, IActionSucceededEvent)
def nameActionSucceededSubscriber(obj, event):
    reindexContainer(obj, event)

@adapter(IPlace, IAfterCheckinEvent)
def placeAfterCheckinSubscriber(obj, event):
    for child in obj.values():
        child.reindexObject()
    reindexContainer(event.object, event)

