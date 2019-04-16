import logging
from . import ContentExportAdapter
from . import PlaceSubObjectExportAdapter
from . import TemporalExportAdapter
from . import WorkExportAdapter
from . import archetypes_getter
from . import get_export_adapter
from . import memoize_all_methods
from . import vocabulary_uri

log = logging.getLogger('PleiadesEntity.adapters.connection')


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
        if target is not None:
            adapter = get_export_adapter(target)
            if adapter is not None:
                return adapter.uri()
            else:
                log.warning(
                    'No export adapter found for connection '
                    '{} to target {}'.format(
                        '/'.join(self.context.getPhysicalPath()), target
                    )
                )
        else:
            log.warning('No connection target found for connection {}'.format(
                '/'.join(self.context.getPhysicalPath())
            ))
        # Raising NotImplementedError skips the bad connection
        raise NotImplementedError
