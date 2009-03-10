from Acquisition import aq_inner, aq_parent
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from Products.PleiadesEntity.content.interfaces import ILocation, IName, IFeature, IPlace
from pleiades.transliteration import transliterate_name


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
    featureChangeSubscriber(f, event)
    
@adapter(ILocation, IObjectModifiedEvent)
def locationChangeSubscriber(obj, event):
    obj.reindexObject()
    x = aq_inner(obj)
    f = aq_parent(x)
    featureChangeSubscriber(f, event)

@adapter(IFeature, IObjectModifiedEvent)
def featureChangeSubscriber(obj, event):
    obj.reindexObject()
    for p in obj.getBRefs('feature_place'):
        p.reindexObject()


