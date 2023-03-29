from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
import requests


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


class QueryBibliographicData(BrowserView):
    def __call__(self):
        response =  requests.get("https://api.zotero.org/groups/2533/items", params={"q": self.request.get('q')})
        return response.text
