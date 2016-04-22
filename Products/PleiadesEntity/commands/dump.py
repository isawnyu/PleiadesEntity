from Products.CMFCore.utils import getToolByName
from Products.PleiadesEntity.browser.adapters import get_export_adapter
from Products.PleiadesEntity.browser.formatters.as_json import JSONFormatter
from Testing.makerequest import makerequest
import sys


BATCH_SIZE = 100
FORMATTERS = (
    JSONFormatter,
)


def iterate_places(site):
    p_jar = site._p_jar
    catalog = getToolByName(site, 'portal_catalog')
    i = 0
    for brain in catalog.unrestrictedSearchResults(portal_type='Place'):
        yield brain.getObject()

        # minimize ZODB cache periodically
        i += 1
        if not i % BATCH_SIZE:
            p_jar.cacheMinimize()


def dump(app, outfolder):
    app = makerequest(app)
    site = app.plone
    app.REQUEST.setServerURL('http', 'pleiades.stoa.org')
    app.REQUEST.other['VirtualRootPhysicalPath'] = site.getPhysicalPath()

    formatters = []
    for formatter_cls in FORMATTERS:
        formatter = formatter_cls(outfolder)
        formatters.append(formatter)
        formatter.start()

    for place in iterate_places(site):
        __traceback_info__ = '/'.join(place.getPhysicalPath())
        adapter = get_export_adapter(place)
        for formatter in formatters:
            formatter.dump_one(adapter)

    for formatter in formatters:
        formatter.finish()


# This script is meant to be run using zopectl, e.g.
# bin/instance -Oplone run dump.py [outfolder]
if __name__ == '__main__':
    outfolder = sys.argv[-1]
    dump(app, outfolder)
