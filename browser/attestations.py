
import logging

from Acquisition import aq_inner, aq_parent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from contentratings.interfaces import IUserRating
from plone.memoize import view
from zope.component import getAdapters, getMultiAdapter

from zgeo.geographer.interfaces import IGeoreferenced
from pleiades.geographer.geo import NotLocatedError
from Products.PleiadesEntity.time import to_ad

log = logging.getLogger('Products.PleiadesEntity')


class TimeSpanWrapper(object):
    
    def __init__(self, context):
        self.context = context

    @property
    def timeSpan(self):
        try:
            trange = self.context.temporalRange()
            if trange:
                return {'start': int(trange[0]), 'end': int(trange[1])}
            else:
                return None
        except AttributeError:
            return None

    @property
    def timeSpanAD(self):
        span = self.timeSpan
        if span:
            return dict([(k, to_ad(v)) for k, v in span.items()])
        else:
            return None

    @property
    def snippet(self):
        timespan = self.timeSpanAD
        if timespan and timespan['end'] == "AD 2100":
            timespan['end'] = "Present"
        return (timespan and "%(start)s - %(end)s" % timespan
            ) or "Attested dates needed"


class PlacefulAttestations(BrowserView):

    @property
    @view.memoize
    def names(self):
        results = []
        for ob in self.context.getNames():
            results.append((ob, TimeSpanWrapper(ob).snippet))
        return results

    @property
    @view.memoize
    def locations(self):
        results = []
        for ob in self.context.getLocations():
            results.append((ob, TimeSpanWrapper(ob).snippet))
        return results

class ChildrenTable(BrowserView):
    """table of locations or names
    """
    def __call__(self):
        self.wftool = getToolByName(self.context, "portal_workflow")
        self.vtool = getToolByName(self.context, 'portal_vocabularies')
        self.iterate = self.context.restrictedTraverse("@@iterate")
        portal_state = self.context.restrictedTraverse("@@plone_portal_state")
        children = []
        for ob in self.accessor():
            #category = dict(
            #    getAdapters((ob,), IUserRating)).get('three_stars', 0)
            #avg_rating = float(category and category.averageRating)
            nrefs = len(ob.getReferenceCitations())
            #score = (avg_rating + 1.0)*(nrefs + 1.0)
            span = TimeSpanWrapper(ob).timeSpan
            if span:
                score = span['start']
            else:
                score = 2112
            children.append((score, ob, nrefs))
        if len(children) == 0 and portal_state.anonymous():
            rows = ['<span class="emptyChildItem"><em>None</em></span>']
        else:
            rows = self.rows(children)
        return u'<p class="placeChildren">' + ''.join(rows) + '</p>'

class LocationsTable(ChildrenTable):
    def accessor(self):
        return self.context.getLocations()
    def snippet(self, ob):
        parts = []
        try:
            parts.append(IGeoreferenced(ob).type)
        except (ValueError, NotLocatedError):
            parts.append("unlocated")
        parts.append(TimeSpanWrapper(ob).snippet)
        return "; ".join(parts)
    def rows(self, locations):
        output = []
        where_tag = "where"
        if self.iterate and self.iterate()['working_copy'] is not None:
            where_tag = "baseline-where"
        for score, ob, nrefs in sorted(locations, reverse=False):
            innerHTML = [
                u'<span id="%s_%s" class="placeChildItem Location" title="%s">' % (
                    ob.getId(),
                    where_tag,
                    self.snippet(ob) + "; " + unicode(ob.Description(), "utf-8") ),
                u'<a class="state-%s" href="%s">%s</a>' % (
                     self.wftool.getInfoFor(ob, 'review_state'), 
                     ob.absolute_url(), 
                     unicode(
                        ob.Title(), 'utf-8') + u" (copy)" * (
                            "copy" in ob.getId())),
                u'</span>' ]
            output.append(u"".join(innerHTML))
        return u'<p class="placeChildren">' + ', '.join(output) + '</p>'


class NamesTable(ChildrenTable):
    """table of locations
    """
    def accessor(self):
        return self.context.getNames()
    def snippet(self, ob):
        parts = []
        if ob.getNameLanguage():
            parts.append(self.langs[ob.getNameLanguage()])
        parts.append(TimeSpanWrapper(ob).snippet)
        return "; ".join(parts)
    def postfix(self, ob):
        acert = ob.getAssociationCertainty();
        if acert == 'less-certain':
            return u'?'
        elif acert == 'uncertain':
            return u'??'
        return u''
    def rows(self, names):
        vocab = self.vtool.getVocabularyByName('ancient-name-languages')
        self.langs = dict(vocab.getDisplayList(vocab).items())
        output = []
        for score, ob, nrefs in sorted(names, reverse=False):
            nameAttested = ob.getNameAttested() or None
            title = ob.Title() or "Untitled"
            if nameAttested:
                label, label_class = unicode(
                    nameAttested, "utf-8"), "nameAttested"
            else:
                label, label_class = unicode(
                    title, "utf-8"), "nameUnattested"
            innerHTML = [
                u'<span id="%s" class="placeChildItem" title="%s">' % (ob.getId(), self.snippet(ob) + "; " + unicode(ob.Description(), "utf-8")),
                u'<a class="state-%s %s" href="%s">%s%s</a>' % (
                     self.wftool.getInfoFor(ob, 'review_state'), 
                     label_class,
                     ob.absolute_url(),
                     label + u" (copy)" * ("copy" in ob.getId()),
                     self.postfix(ob))
                u'</span>' ]
            output.append(u"".join(innerHTML))
        return u'<p class="placeChildren">' + ', '.join(output) + '</p>'

