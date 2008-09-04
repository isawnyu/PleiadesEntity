from Acquisition import aq_inner, aq_parent
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from Products.PleiadesEntity.content.interfaces import ITemporalAttestation \
    , ILocation, IName, IFeature, IPlace


@adapter(ITemporalAttestation, IObjectModifiedEvent)
def timePeriodChangeSubscriber(obj, event):
    child = aq_inner(obj)
    while 1:
        ob = aq_parent(child)
        if ILocation.providedBy(ob):
            ob.reindexObject()
            locationChangeSubscriber(ob, event)
        elif IName.providedBy(ob):
            ob.reindexObject()
            nameChangeSubscriber(ob, event)
        elif IFeature.providedBy(ob):
            ob.reindexObject()
            featureChangeSubscriber(ob, event)
        elif IPlace.providedBy(ob):
            ob.reindexObject()
        else:
            break
        child = ob

@adapter(IName, IObjectModifiedEvent)
def nameChangeSubscriber(obj, event):
    for f in obj.getBRefs('hasName'):
        f.reindexObject()
        featureChangeSubscriber(f, event)
        #for p in f.getBRefs('hasFeature'):
        #    p.reindexObject()

@adapter(ILocation, IObjectModifiedEvent)
def locationChangeSubscriber(obj, event):
    for f in obj.getBRefs('hasLocation'):
        f.reindexObject()
        featureChangeSubscriber(f, event)
        #for p in f.getBRefs('hasFeature'):
        #    p.reindexObject()

@adapter(IFeature, IObjectModifiedEvent)
def featureChangeSubscriber(obj, event):
    for p in obj.getBRefs('hasFeature'):
        p.reindexObject()
