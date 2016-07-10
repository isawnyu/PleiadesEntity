from AccessControl import getSecurityManager
from collective.geo.geographer.interfaces import IGeoreferenced
from pleiades.geographer.geo import NotLocatedError, representative_point
from plone.memoize import view
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.PleiadesEntity.time import to_ad
import logging

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
        return (
            timespan and "%(start)s - %(end)s" % timespan
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
        return u'<ul class="placeChildren">' + u'\n'.join(rows) + '</ul>'


class RepresentativePoint(BrowserView):
    """representative point data
    """

    def __call__(self):
        repr_pt = representative_point(self.context)
        if repr_pt is None:
            return ''
        # GeoJson stores longitude first, followed by latitude
        # This view returns latitude, longitude
        return '%s, %s' % (repr_pt['coords'][1], repr_pt['coords'][0])


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

    def postfix(self, ob):
        timespan = TimeSpanWrapper(ob).snippet
        if timespan.strip() == '':
            timespan = None
        elif timespan.strip() == 'AD 1700 - Present':
            timespan = 'modern'
        if timespan:
            return u' (%s)' % timespan
        else:
            return u''

    def rows(self, locations):
        output = []
        where_tag = "where"
        if self.iterate and self.iterate()['working_copy'] is not None:
            where_tag = "baseline-where"
        wftool = self.wftool
        checkPermission = getSecurityManager().checkPermission
        credit_utils = self.context.unrestrictedTraverse('@@credit_utils')
        for score, ob, nrefs in sorted(locations, reverse=False):
            review_state = wftool.getInfoFor(ob, 'review_state')
            item = ob.Title().decode('utf-8')
            if 'copy' in ob.getId():
                item += u" (copy)"
            if checkPermission('View', ob):
                link = u'<a class="state-%s" href="%s">%s</a>' % (
                    review_state, ob.absolute_url(), item)
            else:
                link = u'<span class="state-%s">%s</span>' % (
                    review_state, item)
            if review_state != 'published':
                user = credit_utils.user_in_byline(ob.Creator())
                status = u' [%s by %s]' % (review_state, user['fullname'].decode('utf-8'))
            else:
                status = u''
            innerHTML = [
                u'<li id="%s_%s" class="placeChildItem Location" title="%s">' % (
                    ob.getId(),
                    where_tag,
                    self.snippet(ob) + "; " + ob.Description().decode("utf-8"),
                ),
                link,
                self.postfix(ob),
                status,
                u'</li>',
            ]
            output.append(u"\n".join(innerHTML))
        return output


class NamesTable(ChildrenTable):
    """table of names and associated information for plone views, sorted by transliterated title
    """

    def accessor(self):
        return self.context.getNames()

    def snippet(self, ob):
        desc = unicode(ob.Description(), "utf-8")
        if len(desc.strip()) == 0:
            return unicode(ob.Title(), "utf-8")
        else:
            return unicode(ob.Title(), "utf-8") + u': ' + desc.strip()

    def postfix(self, ob):
        acert = ob.getAssociationCertainty()
        nameAttested = ob.getNameAttested() or None
        if nameAttested is not None:
            nameAttested = unicode(nameAttested, "utf-8")
            nameTransliterated = ob.Title() or None
            if nameTransliterated is not None:
                nameTransliterated = unicode(nameTransliterated, "utf-8")
                if nameTransliterated == nameAttested:
                    nameTransliterated = None
        else:
            nameTransliterated = None
        timespan = TimeSpanWrapper(ob).snippet
        if timespan.strip() == '':
            timespan = None
        elif timespan.strip() == 'AD 1700 - Present':
            timespan = 'modern'
        if timespan and nameTransliterated:
            annotation = u'(%s; %s)' % (nameTransliterated, timespan)
        elif nameTransliterated:
            annotation = u'(%s)' % nameTransliterated
        elif timespan:
            annotation = u'(%s)' % timespan
        else:
            annotation = None
        if acert == 'less-certain':
            return [u'?', u' %s?' % annotation][annotation is not None]
        elif acert == 'uncertain':
            return [u'??', u' %s??' % annotation][annotation is not None]
        else:
            return [u'', u' %s' % annotation][annotation is not None]

    def rows(self, names):
        output = []
        wftool = self.wftool
        checkPermission = getSecurityManager().checkPermission
        credit_utils = self.context.unrestrictedTraverse('@@credit_utils')
        for score, ob, nrefs in sorted(names, key=lambda k: k[1].Title() or ''):
            nameAttested = ob.getNameAttested() or None
            title = ob.Title() or "Untitled"
            if nameAttested:
                label, label_class = unicode(
                    nameAttested, "utf-8"), "nameAttested"
            else:
                label, label_class = unicode(
                    title, "utf-8"), "nameUnattested"
            labelLang = ob.getNameLanguage() or "und"
            review_state = wftool.getInfoFor(ob, 'review_state')
            item = u'<span lang="%s">%s</span>' % (
                labelLang,
                label + u" (copy)" * ("copy" in ob.getId()),
            )
            if checkPermission('View', ob):
                link = '<a class="state-%s %s" href="%s">%s</a>' % (
                    review_state, label_class, ob.absolute_url(), item)
            else:
                link = '<span class="state-%s %s">%s</span>' % (
                    review_state, label_class, item)
            if review_state != 'published':
                user = credit_utils.user_in_byline(ob.Creator())
                status = u' [%s by %s]' % (review_state, user['fullname'].decode('utf-8'))
            else:
                status = u''
            innerHTML = [
                u'<li id="%s" class="placeChildItem" title="%s">' % (
                    ob.getId(), self.snippet(ob)),
                link,
                self.postfix(ob),
                status,
                u'</li>',
            ]
            output.append(u"\n".join(innerHTML))
        return output
