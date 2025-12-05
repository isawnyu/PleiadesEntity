import json

from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class MapboxSettingsJS(BrowserView):

    def __call__(self):
        registry = getUtility(IRegistry)
        token = registry.get("pleiades.mapbox.access_token", u"")
        response = self.request.response
        response.setHeader(
            "Content-Type", "application/javascript;charset=utf-8"
        )
        response.setHeader(
            "Cache-Control", "no-cache, no-store, must-revalidate"
        )
        response.setHeader("Pragma", "no-cache")
        response.setHeader("Expires", "0")

        script = u"window.PLEIADES_MAPBOX_TOKEN = %s;\n" % (
            json.dumps(token or u"")
        )
        return script
