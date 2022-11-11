from collections import defaultdict
from AccessControl import getSecurityManager
from Acquisition import aq_parent
from collective.geo.geographer.interfaces import IGeoreferenced
from pleiades.geographer.geo import NotLocatedError, representative_point
from pleiades.vocabularies.vocabularies import get_vocabulary
from plone.batching import Batch
from plone.memoize import view
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
        location_types = [
            "associated_modern",
            "relocated_modern",
            "central_point",
            "legacy",
            "representative",
        ]
        labeled_locations = defaultdict(set)
        for _, ob, _ in sorted(locations, reverse=False):
            current_location_types = ob.getLocationType()
            found = False
            for location_type in location_types:
                if location_type in current_location_types:
                    labeled_locations[location_type].add(ob)
                    found = True
                    break
            if not found:
                labeled_locations['representative'].add(ob)
        for location_type in location_types:
            if not labeled_locations[location_type]:
                continue
            if location_type == "central_point":
                location_title = "Central Point"
            else:
                location_title = location_type.replace('_', ' ').title() + " Locations"
            output.append(u"<li><b>%s:</b>\n<ul>" % location_title)
            for ob in labeled_locations[location_type]:
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
            output.append(u"</li>")
        if any(labeled_locations.items()):
            output.append(u"</ul>")
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
        return [u'', u' %s' % annotation][annotation is not None]

    def prefix(self, ob):
        return AssociationCertaintyWrapper(ob).snippet

    def rows(self, names):
        output = []
        wftool = self.wftool
        checkPermission = getSecurityManager().checkPermission
        credit_utils = self.context.unrestrictedTraverse('@@credit_utils')

        vocabulary = get_vocabulary('ancient_name_languages')
        lang_vocab = {t['id']: t['title'] for t in vocabulary}
        vocabulary = get_vocabulary('name_types')
        ntype_titles = {t['id']: t['title'] for t in vocabulary}
        ntype_vocab_sorted = sorted([t['id'] for t in vocabulary if t['id'] not in ['ethnic', 'geographic']])
        ntype_vocab_sorted.insert(0, 'ethnic')
        ntype_vocab_sorted.insert(0, 'geographic')
        prepend = ', '.join(ntype_vocab_sorted)
        for ntype in ntype_vocab_sorted:
            these_names = [n for n in names if n[1].getNameType() == ntype]
            if len(these_names) == 0:
                continue
            nlabel = ntype_titles[ntype]
            if nlabel.endswith('name'):
                nlabel += 's'
            elif nlabel.startswith('name '):
                nlabel = nlabel.replace('name ', 'names ')
            elif nlabel.startswith('label '):
                nlabel = nlabel.replace('label ', 'labels ')
            if '(' in nlabel:
                nlabel = nlabel.split('(')
                nlabel = '('.join([nlabel[0].title(), nlabel[1]])
            else:
                nlabel = nlabel.title()
            outerHTML = [
                u'<li id="{}" class="placeChildItem">'.format(ntype),
                u'<label>{}:</label>'.format(nlabel),
                u'<ul>'
            ]
            for score, ob, nrefs in sorted(these_names, key=lambda k: k[1].Title() or ''):
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
                    try:
                        lang_title = lang_vocab[labelLang]
                    except KeyError as err:
                        msg = (
                            'Invalid identifier "{}" for language in name "{}"\n{}'
                            ''.format(labelLang, ob.absolute_url(), err.message))
                        raise KeyError(msg)
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
                outerHTML.extend(innerHTML)
            outerHTML.append(u'</ul></li> <!-- placeChildItem {} -->'.format(ntype))
            output.append(u"\n".join(outerHTML))
            output.append(u"<!-- {} --->".format(prepend))
        return output


class ConnectionsTable(ChildrenTable):
    """table of connections and associated information for plone views
    """

    def accessor(self):
        return self.context.getSubConnections()

    def snippet(self, ob):
        return unicode(self.referenced(ob).Title(), "utf-8")

    @view.memoize
    def referer(self, ob):
        return aq_parent(ob)

    @view.memoize
    def referenced(self, ob):
        return ob.getConnection()

    def prefix(self, ob):
        acert = AssociationCertaintyWrapper(ob).snippet
        return u"{}".format(acert)

    def postfix(self, ob):
        timespan = TimeSpanWrapper(ob).snippet
        if timespan.strip() == '':
            timespan = None
        elif timespan.strip() == 'AD 1700 - Present':
            timespan = 'modern'
        if timespan:
            annotation = u'(%s)' % timespan
        else:
            annotation = u''
        review_state = self.wftool.getInfoFor(ob, 'review_state')
        if review_state != 'published':
            credit_utils = self.context.unrestrictedTraverse('@@credit_utils')
            user = credit_utils.user_in_byline(ob.Creator())
            status = u' [connection %s by %s]' % (review_state, user['fullname'].decode('utf-8'))
            annotation += u' {}'.format(status)
        annotation = annotation.strip()
        return annotation

    def subject(self, ob):
        return self.referer(ob)

    def subject_phrase(self, ob):
        subject = self.subject(ob)
        label = unicode(subject.Title(), 'utf-8')
        review_state = self.wftool.getInfoFor(subject, 'review_state')
        attributes = {
            'class': u'connection-subject state-{}'.format(review_state),
            'title': u'subject of this connection: {}'.format(label)
        }
        if self.context.getId() != subject.getId():
            tag = u'a'
            attributes['href'] = subject.absolute_url()
        else:
            tag = u'span'
        return self.taggify(tag, attributes, label)

    def verb(self, ob):
        vocabulary = get_vocabulary('relationship_types')
        ctype_dict = {t['id']: t['title'] for t in vocabulary}
        ctype = ob.getRelationshipType()
        if type(ctype) is list:
            ctype = ctype[0]
        return ctype_dict.get(ctype)

    def verb_phrase(self, ob):
        label = self.verb(ob)
        tag = u'a'
        review_state = self.wftool.getInfoFor(ob, 'review_state')
        attributes = {
            'class': u'connection-verb state-{}'.format(review_state),
            'href': ob.absolute_url()
        }
        return self.taggify(tag, attributes, label)

    def predicate(self, ob):
        return self.referenced(ob)

    def predicate_phrase(self, ob):
        predicate = self.predicate(ob)
        try:
            title = predicate.Title()
        except AttributeError:
            if predicate is None:
                log.info(
                    'Connection has no target place resource: {}'
                    ''.format(ob.absolute_url()))
            else:
                log.info(
                    'Unexpected lack of title for connection: {}'
                    ''.format(ob.absolute_url()))
            label = '(???)'
            attributes = {
                'class': u'connection-predicate'
            }
            tag = u'span'
        else:
            label = unicode(title, 'utf-8')
            review_state = self.wftool.getInfoFor(predicate, 'review_state')
            attributes = {
                'class': u'connection-predicate state-{}'.format(review_state),
                'title': u'predicate of this connection: {}'.format(label)
            }
            if self.context.getId() != predicate.getId():
                tag = u'a'
                attributes['href'] = predicate.absolute_url()
            else:
                tag = u'span'
        return self.taggify(tag, attributes, label)

    def taggify(self, tag, attributes, label):
        attrs = [u'{} = "{}"'.format(k, v) for k, v in attributes.items()]
        result = (
            u'<{tag} {attributes}>{label}</{tag}>'
            u''.format(
                tag=tag,
                attributes=u' '.join(attrs),
                label=label))
        return result

    def rows(self, connections):
        sorted_by_title = sorted(connections, key=lambda k: k[1].Title() or '')
        output = self.build_rows(sorted_by_title)

        return output

    def build_rows(self, connections):
        output = []
        portal_state = self.context.restrictedTraverse("@@plone_portal_state")
        anonymous = portal_state.anonymous()
        for score, ob, nrefs in connections:
            if anonymous:
                review_state = self.wftool.getInfoFor(ob, 'review_state')
                if review_state != 'published':
                    continue
                review_state = self.wftool.getInfoFor(self.referer(ob), 'review_state')
                if review_state != 'published':
                    continue
                review_state = self.wftool.getInfoFor(self.referenced(ob), 'review_state')
                if review_state != 'published':
                    continue
            parts = []
            parts.append(
                u'<li id="{id}" class="placeChildItem" title="{title}">'
                u''.format(
                    id=ob.getId(),
                    title=unicode(ob.Title(), 'utf-8')))
            parts.append(self.prefix(ob))
            parts.append(self.subject_phrase(ob))
            parts.append(self.verb_phrase(ob))
            parts.append(self.predicate_phrase(ob))
            parts.append(self.postfix(ob))
            parts.append(u'</li>')
            output.append(u"\n".join(parts))
        return output


class ReverseConnectionsTable(ConnectionsTable):

    def accessor(self):
        return self.context.getReverseConnections()

    @view.memoize
    def referenced(self, ob):
        return aq_parent(ob)

    @view.memoize
    def referer(self, ob):
        return ob.getConnection()

    def subject(self, ob):
        return self.referenced(ob)

    def predicate(self, ob):
        return self.referer(ob)

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
            sorted_by_subject_title = sorted(
                children, key=lambda c: self.subject(c[1]).Title() or ''
            )
            rows = self.build_rows(sorted_by_subject_title)
        b_start = self.request.form.get('b_start', '0')
        batch = Batch(rows, 50, int(b_start), orphan=5)
        return batch
