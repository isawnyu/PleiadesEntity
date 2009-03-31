import transaction
from Products.CMFCore.utils import getToolByName

indexes = [
    ('getTimePeriods', 'KeywordIndex'),
    ]

columns = ['getTermKey', 'getTermValue']

EXTENSION_PROFILES = ('Products.PleiadesEntity:default',)

def install(self):
    portal_quickinstaller = getToolByName(self, 'portal_quickinstaller')
    portal_setup = getToolByName(self, 'portal_setup')
    for extension_id in EXTENSION_PROFILES:
        portal_setup.runAllImportStepsFromProfile(
            'profile-%s' % extension_id, purge_old=False
            )
        product_name = extension_id.split(':')[0]
        portal_quickinstaller.notifyInstalled(product_name)
        transaction.savepoint()

def xinstall(self):
    """
    custom installation steps
    """
    out = []
    portal = self.portal_url.getPortalObject()
    for iname, itype in indexes:
        addIndex(portal, out, iname, itype) 
        
    # Vocab catalog metadata
    catalog_tool = getToolByName(portal, 'portal_catalog', None)
    for name in columns:
        addColumn(catalog_tool, name)

    return out
    
def addColumn(tool, name):
    try:
        tool.manage_addColumn(name)
    except:
        pass

def addIndex(portal, out, name, type):
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        try:
            index = catalog._catalog.getIndex(name)
        except KeyError:
            pass
        else:
            indextype = index.__class__.__name__
            if indextype == type:
                return 0
            catalog.delIndex(name)
            out.append("Deleted %s" % indextype + " '%s' from portal_catalog." % name)

        catalog.addIndex(name, type)
        out.append("Added %s" % type + " '%s' to portal_catalog." % name)
        return 1 # Ask for reindexing
    return 0    
    
