# module

from Acquisition import aq_inner, aq_parent
from Products.Five.browser import BrowserView

from Products.PleiadesEntity.content.interfaces import IPlace

class PlaceFinder(BrowserView):

    def __call__(self):
        ob = self.context
        while ob:
            if IPlace.providedBy(ob):
                break
            ob = aq_parent(aq_inner(ob))
        return ob

