from ..interfaces import IExportAdapter
from zope.component import queryAdapter
from zope.interface import implementer


def get_export_adapter(ob):
    return queryAdapter(ob, IExportAdapter)


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
