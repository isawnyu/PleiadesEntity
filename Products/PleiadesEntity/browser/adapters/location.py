from Products.PleiadesEntity.time import to_ad
from . import ContentExportAdapter
from . import PlaceSubObjectExportAdapter
from . import TemporalExportAdapter
from . import CertaintyExportAdapter
from . import WorkExportAdapter
from . import archetypes_getter
from . import vocabulary_uri
from . import memoize_all_methods
from plone import api


@memoize_all_methods
class LocationExportAdapter(
        WorkExportAdapter, TemporalExportAdapter, ContentExportAdapter,
        CertaintyExportAdapter, PlaceSubObjectExportAdapter):

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
    featureTypeURI = vocabulary_uri('place-types', 'featureType')
    details = archetypes_getter('text')
    archaeologicalRemains = archetypes_getter('archaeologicalRemains')
    locationType = archetypes_getter('locationType')
    locationTypeURI = vocabulary_uri('location-types', 'locationType')

    _accuracy = archetypes_getter('accuracy', raw=False)
    def accuracy(self):
        accuracy = self._accuracy()
        if accuracy is not None:
            return accuracy.absolute_url()

    def accuracy_value(self):
        accuracy = self._accuracy()
        if accuracy is not None:
            accuracy_path = '/'.join(accuracy.getPhysicalPath())
            portal = api.portal.get()
            my_accuracy = portal.restrictedTraverse(accuracy_path)
            v = my_accuracy.getField('value').get(inst)
            return v
            




