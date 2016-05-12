from pleiades.geographer.geo import extent
from pleiades.geographer.geo import representative_point
from shapely.geometry import shape
from . import archetypes_getter
from . import export_children
from . import ContentExportAdapter
from . import WorkExportAdapter
from . import get_export_adapter
from . import export_config
from . import memoize_all_methods
import geojson
import re


@memoize_all_methods
class PlaceExportAdapter(WorkExportAdapter, ContentExportAdapter):

    def _connectsWith(self):
        return self.context.getRefs("connectsWith")

    def _hasConnectionsWith(self):
        return self.context.getBRefs("connectsWith")

    def connectsWith(self):
        return [place.absolute_url() for place
                in (self._connectsWith() + self._hasConnectionsWith())]

    def _reprPoint(self):
        return representative_point(self.context)

    def reprPoint(self):
        reprPoint = self._reprPoint()
        if reprPoint is None:
            return
        return reprPoint['coords']

    @export_config(json=False)
    def locationPrecision(self):
        reprPoint = self._reprPoint()
        if reprPoint is None:
            return
        return reprPoint['precision']

    locations = export_children('Location')
    names = export_children('Name')

    placeTypes = archetypes_getter('placeType')
    rights = archetypes_getter('rights')
    subject = archetypes_getter('subject')
    details = archetypes_getter('text')

    @export_config(json=False)
    def timePeriods(self):
        return self.context.getTimePeriods()

    @export_config(json=False)
    def temporalRange(self):
        return self.context.temporalRange()

    @export_config(json=False)
    def start(self):
        trange = self.temporalRange()
        if trange is None:
            return
        return trange[0]

    @export_config(json=False)
    def end(self):
        trange = self.temporalRange()
        if trange is None:
            return
        return trange[1]

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
        extent = self.extent()
        if extent is None:
            return
        return shape(extent).bounds

    @export_config(json=False)
    def extent(self):
        res = extent(self.context)
        if not res or res['extent'] is None:
            return
        return res['extent']

    @export_config(json=False)
    def geoContext(self):
        note = self.context.getModernLocation()
        if not note:
            note = self.description() or ""
            match = re.search(r"cited: BAtlas (\d+) (\w+)", note)
            if match:
                note = "Barrington Atlas grid %s %s" % (
                    match.group(1), match.group(2).capitalize())
            else:
                note = ""
            note = unicode(note.replace(unichr(174), unichr(0x2194)))
            note = note.replace(unichr(0x2192), unichr(0x2194))
        return note
