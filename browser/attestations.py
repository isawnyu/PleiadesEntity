from Acquisition import aq_inner, aq_parent
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.memoize import view


class PlaceAttestations(BrowserView):
    
    @property
    @view.memoize
    def names(self):
        return [(n, n.getSortedTemporalAttestations()) for n in self.context.getNames()]
        

class FeatureAttestations(PlaceAttestations):
    
    @property
    @view.memoize
    def locations(self):
        return [(n, n.getSortedTemporalAttestations()) for n in self.context.getLocations()]
