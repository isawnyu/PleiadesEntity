from Products.CMFCore.utils import getToolByName

indexes = [('getTimePeriods', 'KeywordIndex')]

def install(self):
     """
       custom installation steps
     """
     
     out = []
     
     portal = self.portal_url.getPortalObject()
     
     for iname, itype in indexes:
         addIndex(portal, out, iname, itype) 
         
     return out
     
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
    
