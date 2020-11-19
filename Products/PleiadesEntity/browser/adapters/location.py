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
import logging
from AccessControl.unauthorized import Unauthorized
logger = logging.getLogger(__name__)


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
            try:
                my_accuracy = portal.restrictedTraverse(accuracy_path)
            except Unauthorized as err:
                msg = (
                    'Access to the referenced accuracy object "{}" is not '
                    'authorized. Context: "{}". {}'.format(
                        accuracy.absolute_url(),
                        self.context.absolute_url(),
                        err.message))
                logger.error(msg)
                return '-1'
            try:
                v = my_accuracy.getField('value').get(my_accuracy)
            except AttributeError as err:
                msg = (
                    'No "value" attribute on referenced accuracy object for '
                    'location at {}. Referenced object "{}" may not be a '
                    'valid "accuracy assessment" object.\n{}'.format(
                        self.context.absolute_url(),
                        accuracy.absolute_url(),
                        err.message))
                logger.error(msg)
                return '-1'
            return v
            




