from plone.app.layout.viewlets import common
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from pleiades.vocabularies.interfaces import IPleiadesSettings
import json


class DefaultWorksViewlet(common.ViewletBase):
    def index(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IPleiadesSettings)
        return "<script>pleiades_default_works = {}</script>".format(json.dumps(settings.default_works))
