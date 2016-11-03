from Acquisition import aq_inner, aq_parent
from plone.app.iterate.interfaces import IAfterCheckinEvent
from Products.CMFCore.interfaces import IActionSucceededEvent, IContentish
from Products.CMFCore.utils import getToolByName
from Products.PleiadesEntity.content.interfaces import IFeature, IPlace
from Products.PleiadesEntity.content.interfaces import ILocation, IName
from Products.PleiadesEntity.time import temporal_overlap
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import logging

log = logging.getLogger('PleiadesEntity')


def reindexContainer(obj, event):
    x = aq_inner(obj)
    f = aq_parent(x)
    if IPlace.providedBy(f):
        log.debug("Reindexing container %s", f)
        f.reindexObject()


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
    wt = getToolByName(obj, "portal_workflow")

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
                review_state = wt.getInfoFor(sub, 'review_state')
                if review_state != 'published':
                    continue
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
# Also, we need to make sure the parent has its contributors updated
#
@adapter(ILocation, IActionSucceededEvent)
def locationActionSucceededSubscriber(obj, event):
    log.debug("Event handled: %s, %s", obj, event)
    reindexContainer(obj, event)
    context = aq_inner(obj)
    parent = aq_parent(context)
    if IPlace.providedBy(parent):
        contributorsSubscriber(parent, event)

@adapter(IName, IActionSucceededEvent)
def nameActionSucceededSubscriber(obj, event):
    reindexContainer(obj, event)
    context = aq_inner(obj)
    parent = aq_parent(context)
    if IPlace.providedBy(parent):
        contributorsSubscriber(parent, event)

@adapter(IPlace, IAfterCheckinEvent)
def placeAfterCheckinSubscriber(obj, event):
    for child in obj.values():
        child.reindexObject()
    reindexContainer(event.object, event)

