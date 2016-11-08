from Products.Five import BrowserView
from zExceptions import NotFound
from ..adapters import get_export_adapter
from ..adapters import collect_export_data
import simplejson as json
import os


PRETTY_PRINT = True


def make_ld_context(context_items=None):
    """Returns a JSON-LD Context object.

    See http://json-ld.org/spec/latest/json-ld."""
    ctx = {
        'uri': '@id',

        # Dublin Core
        'dcterms': 'http://purl.org/dc/terms/',
        'title': 'dcterms:title',
        'description': 'dcterms:description',
        'snippet': 'dcterms:abstract',
        'created': 'dcterms:created',
        'rights': 'dcterms:rights',
        'subject': 'dcterms:subject',
    }
    return ctx


def format_json(adapter, with_context=False):
    data = collect_export_data(adapter)
    if with_context:
        data['@context'] = make_ld_context()
    return json.dumps(
        data, for_json=True, indent=4 if PRETTY_PRINT else None,
        ensure_ascii=False).encode('utf-8')


class JSONFormatter(object):

    def __init__(self, path):
        self.filepath = os.path.join(path, 'pleiades-places.json')
        self.errata_filepath = os.path.join(path, 'pleiades-errata.json')

    def start(self):
        ld_context = json.dumps(
            make_ld_context(), indent=4 if PRETTY_PRINT else None,
            ensure_ascii=False).encode('utf-8')
        header = '''{{
"@context": {},
"@graph": ['''.format(ld_context)

        self.f = open(self.filepath, 'w')
        self.f.write(header)
        self.first_normal = True

        self.errata_f = open(self.errata_filepath, 'w')
        self.errata_f.write(header)
        self.first_errata = True

    def dump_one(self, adapter):
        if adapter.path().startswith('/errata/'):
            if self.first_errata:
                self.first_errata = False
            else:
                self.errata_f.write(',\n')
            self.errata_f.write(format_json(adapter))
        else:
            if self.first_normal:
                self.first_normal = False
            else:
                self.f.write(',\n')
            self.f.write(format_json(adapter))

    def finish(self):
        self.f.write(']}')
        self.f.close()
        self.errata_f.write(']}')
        self.errata_f.close()


class JSONView(BrowserView):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json; charset=utf-8')
        self.request.response.setHeader('Access-Control-Allow-Origin', '*')

        # BBB
        sm = bool(self.request.form.get('sm', 0))
        if sm:
            raise Exception('Support for spherical mercator projection was removed.')

        adapter = get_export_adapter(self.context)
        if adapter is None:
            raise NotFound()

        return format_json(adapter, with_context=True)
