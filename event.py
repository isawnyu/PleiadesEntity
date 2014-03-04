import geojson
import logging

from Acquisition import aq_inner, aq_parent
from plone.app.iterate.interfaces import IAfterCheckinEvent
from Products.CMFCore.interfaces import IActionSucceededEvent, IContentish
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from Products.PleiadesEntity.content.interfaces import ILocation, IName
from Products.PleiadesEntity.content.interfaces import IFeature, IPlace
from Products.PleiadesEntity.time import temporal_overlap
from pleiades.transliteration import transliterate_name
from pleiades.json.browser import getContents, wrap
from pleiades.geographer.geo import extent, representative_point

log = logging.getLogger('PleiadesEntity')

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

def writePlaceJSON(place, event, published_only=True):
    
    # determine the filename to write
    pid = place.getId()
    fn = "/home/zope/pleiades/json/place-%s.json" % pid

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


    # id
    # title
    # description 
    # connectsWith
    # recent_changes
    # reprPoint
    # features
    # names
    # type == FeatureColleciton
    # bbox    

    if published_only:
        contentFilter = {'review_state': 'published'}
    else:
        contentFilter = {}

    #j = wrap(place)

    # Locations
    xs = []
    ys = []
    x = list(getContents(
            place,
            **dict(
                [('portal_type', 'Location')] + contentFilter.items())))

    if len(x) > 0:
        features = [wrap(ob) for ob in x]
    else:
        features = [wrap(ob) for ob in place.getFeatures()] \
                 + [wrap(ob) for ob in place.getParts()]

    try:
        ex = extent(place)
        bbox = shape(ex['extent']).bounds
        precision = ex['precision']
        reprPoint = representative_point(place)['coords']
    except:
        precision = "unlocated"
        bbox = None
        reprPoint = None

    # Names
    objs = sorted(
        getContents(
            place,
            **dict(
                [('portal_type', 'Name')] + contentFilter.items())),
        key=rating, reverse=True)
    names = [o.getNameAttested() or o.getNameTransliterated() for o in objs]

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

