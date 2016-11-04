from plone.batching import Batch
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
        results = catalog.searchResults(UID=uids)

        b_size = int(self.request.form.get('b_size') or 50)
        b_start = int(self.request.form.get('b_start') or 0)
        return Batch(results, b_size, b_start, orphan=5)
