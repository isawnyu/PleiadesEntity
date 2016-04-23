from pleiades.geographer.geo import extent
from plone.memoize import instance
from Products.PleiadesEntity.time import to_ad
from . import ContentExportAdapter
from . import TemporalExportAdapter
from . import WorkExportAdapter
from . import archetypes_getter


class LocationExportAdapter(
        WorkExportAdapter, TemporalExportAdapter, ContentExportAdapter):

    @instance.memoize
    def _extent(self):
        return extent(self.context)

    def geometry(self):
        res = self._extent()
        if not res:
            return
        return res['extent']

    def _precision(self):
        res = self._extent()
        if not res:
            return
        return res['precision']

    def _snippet(self):
        featureTypes = self.context.getFeatureType() or ['unknown']
        s = ', '.join(x.capitalize() for x in featureTypes)

        trange = self.context.temporalRange()
        if trange:
            start = to_ad(int(trange[0]))
            end = to_ad(int(trange[1]))
            s += '; {} - {}'.format(start, end)

        return s

    featureType = archetypes_getter('featureType')
    associationCertainty = archetypes_getter('associationCertainty')
    details = archetypes_getter('text')

    _accuracy = archetypes_getter('accuracy')
    def accuracy(self):
        accuracy = self._accuracy()
        if accuracy is not None:
            return accuracy.absolute_url()
