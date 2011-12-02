from Acquisition import aq_inner, aq_parent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from contentratings.interfaces import IUserRating
from plone.memoize import view
from zope.component import getAdapters, getMultiAdapter


class PlacefulAttestations(BrowserView):
    
    @property
    @view.memoize
    def names(self):
        results = []
        for ob in self.context.getNames():
            results.append((ob, ob.getSortedTemporalAttestations()))
        return results

    @property
    @view.memoize
    def locations(self):
        results = []
        for ob in self.context.getLocations():
            results.append((ob, ob.getSortedTemporalAttestations()))
        return results

class LocationsTable(BrowserView):
    """table of locations
    """
    def __call__(self):
        wftool = getToolByName(self.context, "portal_workflow")
        def getState(ob):
            return wftool.getInfoFor(ob, 'review_state')
        locations = []
        for ob in self.context.getLocations():
            category = dict(getAdapters((ob,), IUserRating))['three_stars']
            avg_rating = category.averageRating
            locations.append((avg_rating, ob, category))
        rows = []
        for rating, ob, category in sorted(locations, reverse=True):
            stars = getMultiAdapter((ob, self.request),
                                   name='user-ratings')()
            classes = ["RatingViewlet"]
            if category.can_write:
                classes.append("Rateable")
            # build inner HTML as unicode, encode at the end
            innerHTML = u'<td valign="top"><div class="%s">\n%s\n</div></td>' % (" ".join(classes), stars)
            innerHTML += u'<td valign="top"><div id="%s" class="PlaceChildItem Location"><a class="state-%s" href="%s">%s</a> (%s)</div></td>' % (ob.getId(), getState(ob), ob.absolute_url(),  unicode(ob.Title(), 'utf-8') + " (copy)" * ("copy" in ob.getId()), ", ".join([a['timePeriod'].capitalize() for a in ob.getSortedTemporalAttestations()]))
            innerHTML = u'\n<tr>%s</tr>' % innerHTML
            rows.append(innerHTML)
        return u'<table class="PlaceChildren Locations">' + ''.join(rows) + '</table>'

class NamesTable(BrowserView):
    """table of locations
    """
    def __call__(self):
        wftool = getToolByName(self.context, "portal_workflow")
        def getState(ob):
            return wftool.getInfoFor(ob, 'review_state')
        names = []
        for ob in self.context.getNames():
            category = dict(getAdapters((ob,), IUserRating))['three_stars']
            avg_rating = category.averageRating
            names.append((avg_rating, ob, category))
        rows = []
        for rating, ob, category in sorted(names, reverse=True):
            stars = getMultiAdapter((ob, self.request),
                                   name='user-ratings')()
            classes = ["RatingViewlet"]
            if category.can_write:
                classes.append("Rateable")
            innerHTML = u'<td valign="top"><div class="%s">\n%s\n</div></td>' % (" ".join(classes), stars)
            innerHTML += u'<td valign="top"><div class="PlaceChildItem"><a class="state-%s" href="%s">%s</a> (%s)</div></td>' % (getState(ob), ob.absolute_url(), unicode(ob.Title(), 'utf-8') + " (copy)" * ("copy" in ob.getId()), ", ".join([a['timePeriod'].capitalize() for a in ob.getSortedTemporalAttestations()]))
            innerHTML = u'\n<tr>%s</tr>' % innerHTML
            rows.append(innerHTML)
        return u'<table class="PlaceChildren Names">' + ''.join(rows) + '</table>'

