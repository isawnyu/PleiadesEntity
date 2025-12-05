from plone.app.layout.viewlets import common
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from pleiades.vocabularies.interfaces import IPleiadesSettings
import json


class DefaultWorksViewlet(common.ViewletBase):
    def index(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IPleiadesSettings)
        pleiades_default_works = {}
        for work in settings.default_works:
            pleiades_default_works[work['short_title']] = work['zotero_uri']
        return "<script>pleiades_default_works = {}</script>".format(json.dumps(pleiades_default_works))


class MapboxSettingsViewlet(common.ViewletBase):

    def render(self):
        return "<script src='{}/@@mapbox-settings.js'></script>".format(self.context.portal_url())
