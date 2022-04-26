from AccessControl import Unauthorized
from DateTime import DateTime
import plone.api
from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
from Products.PleiadesEntity.content.ReferenceCitation import schema as ReferenceSchema
from zope.component import queryAdapter
from zope.component.interfaces import ComponentLookupError
from zope.interface import implementer
import copy
from ..interfaces import IExportAdapter
import inspect
import itertools
import json
import logging
import Missing

log = logging.getLogger('PleiadesEntity.adapters.connection')


def get_export_adapter(ob):
    return queryAdapter(ob, IExportAdapter)


def collect_export_data(adapter):
    # collect all data from adapter
    data = {}
    for k in dir(adapter):
        if k in ('context', 'for_json', 'brain') or k.startswith('_'):
            continue
        getter = getattr(adapter, k)
        export_config = getattr(getter, 'export_config', {})
        if not export_config.get('json', True):
            continue
        try:
            value = getter()
        except NotImplementedError:
            continue
        if value is Missing.Value:
            value = None
        data[k] = value
    return data


def export_config(**kw):
    def decorator(f):
        f.export_config = kw
        return f
    return decorator


def memoize_all_methods(cls):
    for k in cls.__dict__:
        member = getattr(cls, k)
        if inspect.ismethod(member):
            wrapper = instance.memoize(member)
            if hasattr(member, 'export_config'):
                wrapper.export_config = member.export_config
            setattr(cls, k, wrapper)
    return cls


@implementer(IExportAdapter)
class ExportAdapter(object):

    def __init__(self, context):
        self.context = context

    def for_json(self):
        return collect_export_data(self)


def get_member_adapter(mtool, userid):
    if userid == 'T. Elliot':
        userid = 'thomase'
    if userid == 'S. Gillies':
        userid = 'sgillies'
    member = mtool.getMemberById(userid)
    if member is None:
        return NameOnlyMemberExportAdapter(userid)
    else:
        return MemberExportAdapter(member)


@memoize_all_methods
class ContentExportAdapter(ExportAdapter):

    def __init__(self, context):
        self.context = context
        catalog = getToolByName(context, 'portal_catalog')
        rid = catalog.getrid('/'.join(context.getPhysicalPath()))
        try:
            self.brain = catalog._catalog[rid]
        except (TypeError, KeyError):
            log.warn('Could not find catalog brain for {}'.format(
                '/'.join(context.getPhysicalPath())
            ))
            # This will cause queryAdapter to return None
            raise ComponentLookupError

    @export_config(json=False)
    def uid(self):
        return self.brain.UID

    @export_config(json=False)
    def path(self):
        return self.brain.getPath().replace('/plone', '')

    def uri(self):
        return self.brain.getURL()

    def id(self):
        return self.brain.getId

    def title(self):
        return self.brain.Title.decode('utf8')

    def description(self):
        return self.brain.Description.decode('utf8')

    def _mtool(self):
        return getToolByName(self.context, 'portal_membership')

    def creators(self):
        result = []
        mtool = self._mtool()
        for creator in self.brain.listCreators:
            result.append(get_member_adapter(mtool, creator))
        return result

    def contributors(self):
        result = []
        mtool = self._mtool()
        for contributor in self.context.Contributors():
            result.append(get_member_adapter(mtool, contributor))
        return result

    @export_config(json=False)
    def author_names(self):
        names = []
        for adapter in itertools.chain(self.creators(), self.contributors()):
            reverse = len(names) == 0  # first name reversed
            names.append(abbreviate_name(adapter.name(), reverse=reverse))
        return ', '.join(names)

    def created(self):
        return self.brain.created.HTML4()

    @export_config(json=False)
    def modified(self):
        return self.brain.modified.HTML4()

    def review_state(self):
        return self.brain.review_state

    def history(self):
        rt = getToolByName(self.context, "portal_repository")
        if rt is None or not rt.isVersionable(self.context):
            return []
        try:
            history = rt.getHistoryMetadata(self.context)
        except Unauthorized:
            history = None
        if not history:
            return []
        result = []
        # Count backwards from most recent to least recent
        for i in xrange(history.getLength(countPurged=False) - 1, -1, -1):
            revision = history.retrieve(i, countPurged=False)
            meta = revision['metadata']['sys_metadata']
            userid = meta['principal']
            modified = DateTime(meta['timestamp'], 'UTC')
            modified._timezone_naive = True
            result.append({
                'comment': meta['comment'],
                'modified': modified.HTML4(),
                'modifiedBy': userid,
            })
        return result

    @export_config(json=False)
    def current_version(self):
        return self.brain.currentVersion


def portal_type(self):
    return self.brain.Type

setattr(ContentExportAdapter, '@type', portal_type)


def dict_getter(key, prefix=None):
    def get(self):
        __traceback_info__ = key
        value = self.context[key]
        if prefix and isinstance(value, str):
            value = prefix + value
        return value
    get.__name__ = '__get__{}'.format(key)
    return get


def archetypes_getter(fname, raw=True):
    def get(self):
        __traceback_info__ = fname
        inst = self.context
        if raw:
            value = inst.getField(fname).getRaw(inst)
        else:
            value = inst.getField(fname).get(inst)
        if isinstance(value, DateTime):
            value = value.HTML4()
        return value
    get.__name__ = 'get_field_{}'.format(fname)
    return get


def vocabulary_uri(vocab_name, fname):
    def get(self):
        if isinstance(self, dict):
            value = self[fname]
        else:
            value = getattr(self, fname)()
        portal = plone.api.portal.get()
        if isinstance(value, tuple):
            return [
                "{}/{}/{}".format(
                    portal.restrictedTraverse('vocabularies').absolute_url(),
                    vocab_name,
                    subvalue,
                ) for subvalue in value
            ]
        return "{}/{}/{}".format(
            portal.restrictedTraverse('vocabularies').absolute_url(),
            vocab_name,
            value,
        )
    return get


def export_children(portal_type):
    def get(self):
        __traceback_info__ = portal_type
        result = []
        filter = {'portal_type': portal_type}
        for child in self.context.listFolderContents(filter):
            result.append(get_export_adapter(child))
        return result
    get.__name__ = 'get_children_{}'.format(portal_type)
    return get


@memoize_all_methods
class ReferenceExportAdapter(ExportAdapter):
    shortTitle = dict_getter('short_title')
    citationDetail = dict_getter('citation_detail')
    formattedCitation = dict_getter('formatted_citation')
    type = dict_getter('type')
    citationTypeURI = dict_getter(
        'type', prefix='http://purl.org/spar/cito/'
    )

    bibliographicURI = dict_getter('bibliographic_uri')
    accessURI = dict_getter('access_uri')
    alternateURI = dict_getter('alternate_uri')

    def otherIdentifier(self):
        identifier = self.context.get('identifier')
        return identifier if identifier != self.bibliographicURI() else ""


@memoize_all_methods
class WorkExportAdapter(ExportAdapter):
    provenance = archetypes_getter('initialProvenance')
    _references = archetypes_getter('referenceCitations', raw=False)

    def references(self):
        result = []
        for ref in self._references():
            result.append(ReferenceExportAdapter(ref))
        return result


class CertaintyExportAdapter(ExportAdapter):
    associationCertainty = archetypes_getter('associationCertainty')
    associationCertaintyURI = vocabulary_uri('association-certainty', 'associationCertainty')


@memoize_all_methods
class TemporalExportAdapter(ExportAdapter):
    def attestations(self):
        attestations = copy.copy(archetypes_getter('attestations', raw=False)(self))
        for attestation in attestations:
            attestation['timePeriodURI'] = vocabulary_uri('time-periods', 'timePeriod')(attestation)
            attestation['confidenceURI'] = vocabulary_uri('attestation-confidence', 'confidence')(attestation)
        return attestations

    def _temporalRange(self):
        return self.context.temporalRange()

    def start(self):
        trange = self._temporalRange()
        if trange is None:
            return
        return trange[0]

    def end(self):
        trange = self._temporalRange()
        if trange is None:
            return
        return trange[1]


@memoize_all_methods
class MemberExportAdapter(ExportAdapter):

    def uri(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        return portal_url + '/author/' + self.context.getId()

    def username(self):
        return self.context.getId()

    def name(self):
        return self.context.getProperty('fullname', None)

    def homepage(self):
        return self.context.getProperty('homepage', None)


@memoize_all_methods
class NameOnlyMemberExportAdapter(ExportAdapter):

    def username(self):
        return None

    def name(self):
        return self.context


@memoize_all_methods
class PlaceSubObjectExportAdapter(ExportAdapter):

    @export_config(json=False)
    def subject(self):
        return self.context.Subject()

    @export_config(json=False)
    def pid(self):
        return '/'.join(self.context.getPhysicalPath()[:-1]).replace(
            '/plone', '')

    @export_config(json=False)
    def reprPoint(self):
        value = self.brain.reprPt
        if not value:
            return
        coords, precision = value
        return coords

    @export_config(json=False)
    def locationPrecision(self):
        value = self.brain.reprPt
        if not value:
            return
        coords, precision = value
        return precision

    @export_config(json=False)
    def timePeriods(self):
        return self.context.getTimePeriods()

    @export_config(json=False)
    def temporalRange(self):
        return self.context.temporalRange()

    @export_config(json=False)
    def start(self):
        trange = self.temporalRange()
        if trange is None:
            return
        return trange[0]

    @export_config(json=False)
    def end(self):
        trange = self.temporalRange()
        if trange is None:
            return
        return trange[1]

    @export_config(json=False)
    def extent(self):
        fullGeometry = self.context.getGeometryJSON()
        if fullGeometry is not None:
            return json.loads(fullGeometry)

        return self.brain.zgeo_geometry or None

    @export_config(json=False)
    def bbox(self):
        return self.brain.bbox or None


def abbreviate_name(name, reverse=False):
    """Replace first name with initial.

    e.g. Tom Elliott -> T. Elliott

    Or if reverse is True, put the last name first.

    e.g. Tom Elliott -> Elliott, T.
    """
    separator = ' '
    parts = [p.strip() for p in name.split(" ", 1)]
    if len(parts) == 2 and len(parts[0]) > 2:
        parts[0] = parts[0][0] + "."
    if reverse and len(parts) == 2:
        parts = parts[::-1]
        separator = ', '
    return separator.join(parts)
