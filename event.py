import logging

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.interfaces import IActionSucceededEvent
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from Products.PleiadesEntity.content.interfaces import ILocation, IName, IFeature, IPlace
from pleiades.transliteration import transliterate_name

log = logging.getLogger('PleiadesEntity')

@adapter(IName, IObjectModifiedEvent)
def nameChangeSubscriber(obj, event):
    nameAttested = obj.getNameAttested()
    nameLanguage = obj.getNameLanguage()
    if nameAttested and nameLanguage:
        t = transliterate_name(nameLanguage, nameAttested)
        obj.getField('nameTransliterated').set(obj, t)
    obj.getField('title').set(obj, obj.getNameTransliterated())
    obj.reindexObject()
    x = aq_inner(obj)
    f = aq_parent(x)
    f.reindexObject()
    featureChangeSubscriber(f, event)
    
@adapter(ILocation, IObjectModifiedEvent)
def locationChangeSubscriber(obj, event):
    # obj.reindexObject()
    x = aq_inner(obj)
    f = aq_parent(x)
    if IPlace.providedBy(f):
        log.info("Reindexing container %s", f)
        f.reindexObject()
        featureChangeSubscriber(f, event)

@adapter(IFeature, IObjectModifiedEvent)
def featureChangeSubscriber(obj, event):
    for p in obj.getBRefs('hasPart'):
        log.info("Reindexing whole %s", p)
        p.reindexObject()

# We want to reindex containers when locations change state
@adapter(ILocation, IActionSucceededEvent)
def locationActionSucceededSubscriber(obj, event):
    x = aq_inner(obj)
    f = aq_parent(x)
    if IPlace.providedBy(f):
        log.info("Reindexing container %s", f)
        f.reindexObject()
        featureChangeSubscriber(f, event)


