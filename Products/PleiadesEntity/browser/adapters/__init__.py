from ..interfaces import IExportAdapter
from DateTime import DateTime
from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
from zope.component import queryAdapter
from zope.interface import implementer


def get_export_adapter(ob):
    return queryAdapter(ob, IExportAdapter)


def collect_export_data(adapter):
    # collect all data from adapter
    data = {}
    for k in dir(adapter):
        if k == 'context' or k.startswith('_'):
            continue
        try:
            value = getattr(adapter, k)()
        except NotImplementedError:
            continue
        data[k] = value
    return data


@implementer(IExportAdapter)
class ExportAdapter(object):

    def __init__(self, context):
        self.context = context


class ContentExportAdapter(ExportAdapter):

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
            member = mtool.getMemberById(creator)
            if member is not None:
                result.append(MemberExportAdapter(member))
        return result

    def contributors(self):
        result = []
        mtool = self._mtool()
        for contributor in self.context.Contributors():
            member = mtool.getMemberById(contributor)
            if member is not None:
                result.append(MemberExportAdapter(member))
        return result

    def created(self):
        return self.context.created().ISO()

    def review_state(self):
        wtool = getToolByName(self.context, 'portal_workflow')
        return wtool.getInfoFor(self.context, 'review_state')

    def history(self):
        rt = getToolByName(self.context, "portal_repository")
        if rt is None or not rt.isVersionable(self.context):
            return []
        history = rt.getHistoryMetadata(self.context)
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
                'modified': modified.ISO(),
                'modifiedBy': userid,
            })
        return result

def portal_type(self):
    return self.context.Type()

setattr(ContentExportAdapter, '@type', portal_type)


def dict_getter(key):
    def get(self):
        __traceback_info__ = key
        return self.context[key]
    return get


def archetypes_getter(fname):
    def get(self):
        __traceback_info__ = fname
        inst = self.context
        value = inst.getField(fname).get(inst)
        if isinstance(value, DateTime):
            value = value.ISO()
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
    _references = archetypes_getter('referenceCitations')

    def references(self):
        result = []
        for ref in self._references():
            result.append(ReferenceExportAdapter(ref))
        return result


class TemporalExportAdapter(ExportAdapter):
    attestations = archetypes_getter('attestations')


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
