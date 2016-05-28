from Products.PleiadesEntity.time import to_ad
from . import ContentExportAdapter
from . import PlaceSubObjectExportAdapter
from . import TemporalExportAdapter
from . import WorkExportAdapter
from . import archetypes_getter
from . import memoize_all_methods


@memoize_all_methods
class LocationExportAdapter(
        WorkExportAdapter, TemporalExportAdapter, ContentExportAdapter,
        PlaceSubObjectExportAdapter):

    def geometry(self):
        return self.extent()

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

    _accuracy = archetypes_getter('accuracy', raw=False)
    def accuracy(self):
        accuracy = self._accuracy()
        if accuracy is not None:
            return accuracy.absolute_url()
