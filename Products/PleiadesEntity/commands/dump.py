from Products.CMFCore.utils import getToolByName
from Products.PleiadesEntity.browser.adapters import get_export_adapter
from Products.PleiadesEntity.browser.formatters.as_csv import CSVFormatter
from Products.PleiadesEntity.browser.formatters.as_csv import CSVNameFormatter
from Products.PleiadesEntity.browser.formatters.as_csv import CSVLocationFormatter
from Products.PleiadesEntity.browser.formatters.as_json import JSONFormatter
from Testing.makerequest import makerequest
import os
import sys
import time


BATCH_SIZE = 100
# (destination subpath, formatter class)
FORMATTERS = {
    'json': ('json', JSONFormatter, ('Place',)),
    'csv-places': ('dumps', CSVFormatter, ('Place',)),
    'csv-names': ('dumps', CSVNameFormatter, ('Name',)),
    'csv-locations': ('dumps', CSVLocationFormatter, ('Location',)),
}


def iterate_content(site, ptypes=('Place',)):
    p_jar = site._p_jar
    catalog = getToolByName(site, 'portal_catalog')
    i = 0
    for brain in catalog.unrestrictedSearchResults(portal_type=ptypes):
        yield brain.getObject()

        # minimize ZODB cache periodically
        i += 1
        if not i % BATCH_SIZE:
            p_jar.cacheMinimize()
#        if i > 1000:
#            return


def dump(app, outfolder, formatter_paths=('json', 'csv-places')):
    t0 = time.time()
    app = makerequest(app)
    site = app.plone
    app.REQUEST.setServerURL('http', 'pleiades.stoa.org')
    app.REQUEST.other['VirtualRootPhysicalPath'] = site.getPhysicalPath()

    formatters = []
    portal_types = set()
    for name in formatter_paths:
        if name not in FORMATTERS:
            print("Invalid Formatter Id {}".format(name))
            continue
        subpath, formatter_cls, ptypes = FORMATTERS.get(name)
        path = os.path.join(outfolder, subpath)
        if not os.path.exists(path):
            os.makedirs(path)

        formatter = formatter_cls(path)
        formatters.append((formatter, set(ptypes)))
        portal_types.update(ptypes)
        formatter.start()

    i = 0
    for item in iterate_content(site, tuple(portal_types)):
        i += 1
        path = '/'.join(item.getPhysicalPath())
        __traceback_info__ = path
        print('Exporting {}'.format(path))
        adapter = get_export_adapter(item)
        for formatter, ptypes in formatters:
            if item.portal_type in ptypes:
                formatter.dump_one(adapter)

    for formatter, ptypes in formatters:
        formatter.finish()

    t1 = time.time() - t0
    print('Exported {} items'.format(i))
    print('Elapsed: {}s'.format(t1))
    if i > 0:
        print('Per item: {}s'.format(t1 / float(i)))


# This script is meant to be run using zopectl, e.g.
# bin/instance -Oplone run dump.py [outfolder]
if __name__ == '__main__':
    outfolder = sys.argv[-1]
#    import cProfile
#    cProfile.run('dump(app, outfolder)', 'profile')
    dump(app, outfolder)
