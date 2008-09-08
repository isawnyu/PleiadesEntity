from Acquisition import aq_inner, aq_parent
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from Products.PleiadesEntity.content.interfaces import ITemporalAttestation \
    , ILocation, IName, IFeature, IPlace
from Products.PleiadesEntity.Extensions.ws_transliteration import transliterate_name


@adapter(ITemporalAttestation, IObjectModifiedEvent)
def timePeriodChangeSubscriber(obj, event):
    child = aq_inner(obj)
    while 1:
        ob = aq_parent(child)
        if ILocation.providedBy(ob):
            locationChangeSubscriber(ob, event)
        elif IName.providedBy(ob):
            nameChangeSubscriber(ob, event)
        elif IFeature.providedBy(ob):
            featureChangeSubscriber(ob, event)
        elif IPlace.providedBy(ob):
            ob.reindexObject()
        else:
            break
        child = ob

@adapter(IName, IObjectModifiedEvent)
def nameChangeSubscriber(obj, event):
    nameAttested = obj.getNameAttested()
    nameLanguage = obj.getNameLanguage()
    if nameAttested and nameLanguage:
        t = transliterate_name(nameLanguage, nameAttested)
        obj.getField('nameTransliterated').set(obj, t)
    obj.getField('title').set(obj, obj.getNameTransliterated())
    obj.reindexObject()
    for f in obj.getBRefs('hasName'):
        featureChangeSubscriber(f, event)

@adapter(ILocation, IObjectModifiedEvent)
def locationChangeSubscriber(obj, event):
    obj.reindexObject()
    for f in obj.getBRefs('hasLocation'):
        featureChangeSubscriber(f, event)

@adapter(IFeature, IObjectModifiedEvent)
def featureChangeSubscriber(obj, event):
    obj.reindexObject()
    for p in obj.getBRefs('hasFeature'):
        p.reindexObject()


