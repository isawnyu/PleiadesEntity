from Products.PleiadesEntity.time import to_ad
from . import ContentExportAdapter
from . import PlaceSubObjectExportAdapter
from . import TemporalExportAdapter
from . import WorkExportAdapter
from . import archetypes_getter
from . import get_export_adapter
from . import memoize_all_methods
from . import vocabulary_uri


@memoize_all_methods
class ConnectionExportAdapter(
    ContentExportAdapter,
    WorkExportAdapter,
    TemporalExportAdapter,
    PlaceSubObjectExportAdapter):

    associationCertainty = archetypes_getter('associationCertainty')
    details = archetypes_getter('text')

    connectionType = archetypes_getter('relationshipType')
    connectionTypeURI = vocabulary_uri('relationship-types', 'connectionType')

    def connectsTo(self):
        target = self.context.getConnection()
        adapter = get_export_adapter(target)
        return adapter.uri()
