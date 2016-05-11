from ..interfaces import IExportAdapter
from DateTime import DateTime
from AccessControl import Unauthorized
from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
from zope.component import queryAdapter
from zope.interface import implementer
import itertools


def get_export_adapter(ob):
    return queryAdapter(ob, IExportAdapter)


def collect_export_data(adapter):
    # collect all data from adapter
    data = {}
    for k in dir(adapter):
        if k == 'context' or k == 'for_json' or k.startswith('_'):
            continue
        getter = getattr(adapter, k)
        export_config = getattr(getter, 'export_config', {})
        if not export_config.get('json', True):
            continue
        try:
            value = getter()
        except NotImplementedError:
            continue
        data[k] = value
    return data


def export_config(**kw):
    def decorator(f):
        f.export_config = kw
        return f
    return decorator


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


class ContentExportAdapter(ExportAdapter):

    @export_config(json=False)
    def uid(self):
        return self.context.UID()

    @export_config(json=False)
    def path(self):
        return '/'.join(self.context.getPhysicalPath()).replace('/plone', '')

    def uri(self):
        return self.context.absolute_url()

    def id(self):
        return self.context.getId()

    def title(self):
        return self.context.Title().decode('utf8')

    def description(self):
        return self.context.Description().decode('utf8')

    @instance.memoize
    def _mtool(self):
        return getToolByName(self.context, 'portal_membership')

    def creators(self):
        result = []
        mtool = self._mtool()
        for creator in self.context.Creators():
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
        return self.context.created().HTML4()

    @export_config(json=False)
    def modified(self):
        return self.context.modified().HTML4()

    def review_state(self):
        wtool = getToolByName(self.context, 'portal_workflow')
        return wtool.getInfoFor(self.context, 'review_state')

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
        rt = getToolByName(self.context, 'portal_repository')
        if rt is None or not rt.isVersionable(self.context):
            return None
        history = rt.getHistoryMetadata(self.context)
        if not history:
            return None
        return history.getVersionId(None, False)


def portal_type(self):
    return self.context.Type()

setattr(ContentExportAdapter, '@type', portal_type)


def dict_getter(key):
    def get(self):
        __traceback_info__ = key
        return self.context[key]
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
    return get


def export_children(portal_type):
    def get(self):
        __traceback_info__ = portal_type
        result = []
        filter = {'portal_type': portal_type}
        for child in self.context.listFolderContents(filter):
            result.append(get_export_adapter(child))
        return result
    return get


class ReferenceExportAdapter(ExportAdapter):
    uri = dict_getter('identifier')
    shortCitation = dict_getter('range')
    type = dict_getter('type')


class WorkExportAdapter(ExportAdapter):
    provenance = archetypes_getter('initialProvenance')
    _references = archetypes_getter('referenceCitations', raw=False)

    def references(self):
        result = []
        for ref in self._references():
            result.append(ReferenceExportAdapter(ref))
        return result


class TemporalExportAdapter(ExportAdapter):
    attestations = archetypes_getter('attestations', raw=False)

    @instance.memoize
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


class NameOnlyMemberExportAdapter(ExportAdapter):

    def username(self):
        return None

    def name(self):
        return self.context


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
