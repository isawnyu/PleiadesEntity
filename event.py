import logging

from Acquisition import aq_inner, aq_parent
from plone.app.iterate.interfaces import IAfterCheckinEvent
from Products.CMFCore.interfaces import IActionSucceededEvent
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from Products.PleiadesEntity.content.interfaces import ILocation, IName, IFeature, IPlace
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
    nameAttested = obj.getNameAttested()
    nameLanguage = obj.getNameLanguage()
    if nameAttested and nameLanguage:
        t = transliterate_name(nameLanguage, nameAttested)
        obj.getField('nameTransliterated').set(obj, t)
    obj.getField('title').set(obj, obj.getNameTransliterated())
    reindexContainer(obj, event)
    
@adapter(ILocation, IObjectModifiedEvent)
def locationChangeSubscriber(obj, event):
    log.debug("Event handled: %s, %s", obj, event)
    reindexContainer(obj, event)

@adapter(IFeature, IObjectModifiedEvent)
def featureChangeSubscriber(obj, event):
    reindexWhole(obj, event)

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

