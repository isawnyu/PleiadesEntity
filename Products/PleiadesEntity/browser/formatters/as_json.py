from Products.Five import BrowserView
from zExceptions import NotFound
from ..adapters import get_export_adapter
import json


def format_json(adapter):
    # collect all data from adapter
    data = {}
    for k in dir(adapter):
        if k == 'context' or k.startswith('_'):
            continue
        data[k] = getattr(adapter, k)()

    return json.dumps(data)


class JSONView(BrowserView):

    def __call__(self):
        adapter = get_export_adapter(self.context)
        if adapter is None:
            raise NotFound()

        self.request.response.setHeader('Content-Type', 'application/json')
        return format_json(adapter)
