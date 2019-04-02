from Products.PleiadesEntity.time import to_ad
from . import ContentExportAdapter
from . import PlaceSubObjectExportAdapter
from . import TemporalExportAdapter
from . import WorkExportAdapter
from . import archetypes_getter
from . import get_export_adapter
from . import memoize_all_methods


@memoize_all_methods
class ConnectionExportAdapter(
    ContentExportAdapter,
    WorkExportAdapter,
    TemporalExportAdapter,
    PlaceSubObjectExportAdapter):

    associationCertainty = archetypes_getter('associationCertainty')
    details = archetypes_getter('text')

    connectionType = archetypes_getter('relationshipType')

    def connectionTypeURI(self):
        return "{}/relationship-types/{}".format(
            self.context.restrictedTraverse('vocabularies').aq_inner.absolute_url(),
            self.context.getRelationshipType()
        )

    def connectsTo(self):
        target = self.context.getConnection()
        adapter = get_export_adapter(target)
        return adapter.uri()
