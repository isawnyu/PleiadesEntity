from pleiades.geographer.geo import extent
from pleiades.geographer.geo import representative_point
from shapely.geometry import shape
from . import archetypes_getter
from . import export_children
from . import ContentExportAdapter
from . import get_export_adapter
import geojson


class PlaceExportAdapter(ContentExportAdapter):

    def connectsWith(self):
        return [o.absolute_url() for o in self.context.getRefs(
            "connectsWith") + self.context.getBRefs("connectsWith")]

    def reprPoint(self):
        res = representative_point(self.context)
        if not res:
            return
        return res['coords']

    locations = export_children('Location')
    names = export_children('Name')

    placeTypes = archetypes_getter('placeType')
    provenance = archetypes_getter('initialProvenance')
    references = archetypes_getter('referenceCitations')
    rights = archetypes_getter('rights')
    subject = archetypes_getter('subject')
    details = archetypes_getter('text')

    # GeoJSON

    def type(self):
        return 'FeatureCollection'

    def features(self):
        features = []
        for child in self.context.objectValues('Location'):
            adapter = get_export_adapter(child)
            features.append(geojson.Feature(
                id=adapter.id(),
                properties=dict(
                    title=adapter.title(),
                    snippet=adapter._snippet(),
                    description=adapter.description(),
                    link=adapter.uri(),
                    location_precision=adapter._precision(),
                ),
                geometry=adapter.geometry(),
            ))
        return features

    def bbox(self):
        res = extent(self.context)
        if not res:
            return
        return shape(res['extent']).bounds
