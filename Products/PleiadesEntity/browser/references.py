from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView


class ReferenceUtils(BrowserView):

    def getBackrefBrains(self, relationship):
        # Efficiently get UIDs of items with this relationship to self.context
        reftool = getToolByName(self.context, 'reference_catalog')
        refbrains = reftool.getBackReferences(
            self.context, relationship, objects=False)
        uids = [b.sourceUID for b in refbrains]

        # Now get the corresponding portal_catalog brains...
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog.searchResults(UID=uids)
