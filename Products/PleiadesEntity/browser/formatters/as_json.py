from Products.Five import BrowserView
from zExceptions import NotFound
from ..adapters import get_export_adapter
from ..adapters import collect_export_data
from ..interfaces import IExportAdapter
import json


class PleiadesJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if IExportAdapter.providedBy(obj):
            return collect_export_data(obj)
        return super(PleiadesJSONEncoder, self).default(obj)


def format_json(adapter):
    data = collect_export_data(adapter)
    return json.dumps(data, cls=PleiadesJSONEncoder)


class JSONView(BrowserView):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')

        # BBB
        sm = bool(self.request.form.get('sm', 0))
        if sm:
            raise Exception('Support for spherical mercator projection was removed.')

        adapter = get_export_adapter(self.context)
        if adapter is None:
            raise NotFound()

        return format_json(adapter)
