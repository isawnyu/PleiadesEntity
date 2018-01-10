from AccessControl import getSecurityManager
from Acquisition import aq_parent
from collective.geo.geographer.interfaces import IGeoreferenced
from pleiades.geographer.geo import NotLocatedError, representative_point
from pleiades.vocabularies.vocabularies import get_vocabulary
from plone import api
from plone.batching import Batch
from plone.memoize import view
from Products.ATVocabularyManager import NamedVocabulary
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.PleiadesEntity.time import to_ad
import logging


log = logging.getLogger('Products.PleiadesEntity')

class AssociationCertaintyWrapper(object):

    def __init__(self, context):
        self.context = context

    @property
    def snippet(self):
        acert = self.context.getAssociationCertainty()
        if acert == 'certain':
            return u''
        acert_title = (
            u'Association between this {} and the place is '
            u''.format(
                self.context.Type().lower()) +
            u'{}.'.format(
                [u'uncertain', u'less than certain'][acert == 'less-certain']))
        acert_marker = [
            u'Uncertain: ', u'Less than certain: '][acert == 'less-certain']
        return u'<span title="{}">{}</span>'.format(acert_title, acert_marker)


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
            ) or "unspecified date range"


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
        return results

    @property
    @view.memoize
    def connections(self):
        results = []
        for ob in self.context.getSubConnections():
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
        if repr_pt is None or repr_pt['coords'] is None:
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

    def prefix(self, ob):
        return AssociationCertaintyWrapper(ob).snippet

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
                self.prefix(ob),
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

    def postfix(self, ob, lang_note):
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

        if not lang_note:
            ln = None
        else:
            if timespan == 'modern':
                if 'modern' in lang_note.lower():
                    timespan = None
            if '(' in lang_note:
                parts = lang_note.split('(')
                parts[1] = parts[1].replace(')', '').strip()
                parts[1] = parts[1][0].upper() + parts[1][1:]
                ln = ' '.join((parts[1], parts[0].strip()))
            else:
                ln = lang_note

        if nameTransliterated or ln or timespan:
            annotation = u'('
            if nameTransliterated:
                annotation += nameTransliterated
                if timespan or ln:
                    annotation += u': '
            if ln:
                annotation += ln
                if timespan:
                    annotation += u', '
            if timespan:
                annotation += timespan
            annotation += u')'
        else:
            annotation = None
        return [u'', u' %s' % annotation][annotation is not None]


    def prefix(self, ob):
        return AssociationCertaintyWrapper(ob).snippet


    def rows(self, names):
        output = []
        wftool = self.wftool
        checkPermission = getSecurityManager().checkPermission
        credit_utils = self.context.unrestrictedTraverse('@@credit_utils')
        atvm = api.portal.get_tool(name='portal_vocabularies')
        nv = NamedVocabulary('ancient-name-languages')
        lang_vocab = nv.getVocabularyDict(atvm)
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
            if labelLang != "und":
                lang_title = lang_vocab[labelLang]
            else:
                lang_title = None
            innerHTML = [
                u'<li id="%s" class="placeChildItem" title="%s">' % (
                    ob.getId(), self.snippet(ob)),
                self.prefix(ob),
                link,
                self.postfix(ob, lang_title),
                status,
                u'</li>',
            ]
            output.append(u"\n".join(innerHTML))
        return output


class ConnectionsTable(ChildrenTable):
    """table of connections and associated information for plone views
    """

    def accessor(self):
        return self.context.getSubConnections()

    def snippet(self, ob):
        return unicode(self.referenced(ob).Title(), "utf-8")

    @view.memoize
    def referenced(self, ob):
        return ob.getConnection()

    def prefix(self, ob):
        ctype = ob.getRelationshipType()
        if type(ctype) is list:
            if len(ctype) == 1:
                ctype = ctype[0]
            else:
                raise RuntimeError(
                    'Unexpected ctype content while preparing connections '
                    'listing: "{}"'.format(repr(ctype)))
        if ctype == 'connection':
            ctype = u'(unspecified connection type) '
        else:
            vocabulary = get_vocabulary('relationship_types')
            ctype_dict = {t['id']:t['title'] for t in vocabulary}
            val = ctype_dict[ctype]
            log.info('type of val is {}'.format(type(val)))
            ctype = u'{} was {} '.format(aq_parent(ob).Title(), ctype_dict[ctype])
        acert = AssociationCertaintyWrapper(ob).snippet
        return u"{}{}".format(acert, ctype)

    def postfix(self, ob):
        timespan = TimeSpanWrapper(ob).snippet
        if timespan.strip() == '':
            timespan = None
        elif timespan.strip() == 'AD 1700 - Present':
            timespan = 'modern'
        if timespan:
            annotation = u'(%s)' % timespan
        else:
            annotation = None
        if annotation:
            return u' {}'.format(annotation)
        else:
            return u''


    def rows(self, connections):
        portal_state = self.context.restrictedTraverse("@@plone_portal_state")
        output = []
        wftool = self.wftool
        checkPermission = getSecurityManager().checkPermission
        credit_utils = self.context.unrestrictedTraverse('@@credit_utils')
        for score, ob, nrefs in sorted(connections, key=lambda k: k[1].Title() or ''):
            referenced = self.referenced(ob)
            label, label_class = self.snippet(ob), "connection"
            review_state = wftool.getInfoFor(ob, 'review_state')
            item = label + u" (copy)" * ("copy" in ob.getId())
            if checkPermission('View', ob):
                if portal_state.anonymous():
                    url = referenced.absolute_url()
                else:
                    url = ob.absolute_url()
                link = '<a class="state-%s %s" href="%s">%s</a>' % (
                    review_state, label_class, url, item)
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
                self.prefix(ob),
                link,
                self.postfix(ob),
                status,
                u'</li>',
            ]
            output.append(u"\n".join(innerHTML))
        return output


class ReverseConnectionsTable(ConnectionsTable):

    def accessor(self):
        return self.context.getReverseConnections()

    @view.memoize
    def referenced(self, ob):
        return aq_parent(ob)

    def batched_rows(self):
        self.wftool = getToolByName(self.context, "portal_workflow")
        self.vtool = getToolByName(self.context, 'portal_vocabularies')
        self.iterate = self.context.restrictedTraverse("@@iterate")
        portal_state = self.context.restrictedTraverse("@@plone_portal_state")
        children = []
        for ob in self.accessor():
            nrefs = len(ob.getReferenceCitations())
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
        b_start = self.request.form.get('b_start', '0')
        batch = Batch(rows, 50, int(b_start), orphan=5)
        return batch
