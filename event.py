import logging

from Acquisition import aq_inner, aq_parent
from plone.app.iterate.interfaces import IAfterCheckinEvent
from Products.CMFCore.interfaces import IActionSucceededEvent, IContentish
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from Products.PleiadesEntity.content.interfaces import ILocation, IName
from Products.PleiadesEntity.content.interfaces import IFeature, IPlace
from pleiades.transliteration import transliterate_name

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

@adapter(IName, IObjectModifiedEvent)
def nameChangeSubscriber(obj, event):
    obj.getField('title').set(
        obj, obj.getNameTransliterated().split(',')[0].strip() or "Untitled")
    reindexContainer(obj, event)
    
@adapter(ILocation, IObjectModifiedEvent)
def locationChangeSubscriber(obj, event):
    log.debug("Event handled: %s, %s", obj, event)
    reindexContainer(obj, event)

@adapter(IFeature, IObjectModifiedEvent)
def featureChangeSubscriber(obj, event):
    reindexWhole(obj, event)

@adapter(IContentish, IObjectModifiedEvent)
def contributorsSubscriber(obj, event):
    # Ensure that principals from the obj's version history are represented
    # in the Contributors field.
    def fixSeanTom(p):
        if p == "T. Elliott":
            return "thomase"
        elif p in ("S. Gillies", "admin"):
            return "sgillies"
        else:
            return p
    creators = set(map(fixSeanTom, obj.Creators()))
    contributors = set(filter(
        lambda x: x not in creators, 
        map(fixSeanTom, obj.Contributors())))
    credited = creators.union(contributors)
    try:
        principals = set()
        context = aq_inner(obj)
        rt = getToolByName(context, "portal_repository")
        history = rt.getHistoryMetadata(context)
        if history:
            for i in range(len(history)):
                metadata = history.retrieve(i)['metadata']['sys_metadata']
                principals.add(metadata['principal'])
        uncredited = principals - credited
        obj.update(
            creators=list(creators), 
            contributors=list(contributors.union(uncredited)))
        obj.reindexObject(idxs=['Creator', 'Contributors'])
    except:
        log.error(
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

