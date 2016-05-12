from Products.CMFCore.utils import getToolByName
from Products.PleiadesEntity.browser.adapters import get_export_adapter
from Products.PleiadesEntity.browser.formatters.as_csv import CSVFormatter
from Products.PleiadesEntity.browser.formatters.as_json import JSONFormatter
from Testing.makerequest import makerequest
import os
import sys
import time


BATCH_SIZE = 100
# (destination subpath, formatter class)
FORMATTERS = (
    ('json', JSONFormatter),
    ('dumps', CSVFormatter),
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
#        if i > 1000:
#            return


def dump(app, outfolder, formatter_classes=FORMATTERS):
    t0 = time.time()
    app = makerequest(app)
    site = app.plone
    app.REQUEST.setServerURL('http', 'pleiades.stoa.org')
    app.REQUEST.other['VirtualRootPhysicalPath'] = site.getPhysicalPath()

    formatters = []
    for subpath, formatter_cls in formatter_classes:
        path = os.path.join(outfolder, subpath)
        if not os.path.exists(path):
            os.makedirs(path)

        formatter = formatter_cls(path)
        formatters.append(formatter)
        formatter.start()

    for place in iterate_places(site):
        path = '/'.join(place.getPhysicalPath())
        __traceback_info__ = path
        print('Exporting {}'.format(path))
        adapter = get_export_adapter(place)
        for formatter in formatters:
            formatter.dump_one(adapter)

    for formatter in formatters:
        formatter.finish()

    print 'Elapsed: {}s'.format(time.time() - t0)


# This script is meant to be run using zopectl, e.g.
# bin/instance -Oplone run dump.py [outfolder]
if __name__ == '__main__':
    outfolder = sys.argv[-1]
#    import cProfile
#    cProfile.run('dump(app, outfolder)', 'profile')
    dump(app, outfolder)
