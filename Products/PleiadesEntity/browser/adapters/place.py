from Products.PleiadesEntity.time import periodRanges
from zope.globalrequest import getRequest
from pleiades.vocabularies.vocabularies import get_vocabulary
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
        return getattr(self.brain, 'connectsWith', None) or []

    def _hasConnectionsWith(self):
        return getattr(self.brain, 'hasConnectionsWith', None) or []

    def connectsWith(self):
        return [
            'https://pleiades.stoa.org/places/{}'.format(id)
            for id in (self._connectsWith() + self._hasConnectionsWith())
        ]

    connections = export_children('Connection')

    def reprPoint(self):
        value = self.brain.reprPt
        if not value:
            return
        coords, precision = value
        return coords

    @export_config(json=False)
    def locationPrecision(self):
        value = self.brain.reprPt
        if not value:
            return
        coords, precision = value
        return precision

    locations = export_children('Location')
    names = export_children('Name')

    rights = archetypes_getter('rights')
    details = archetypes_getter('text')

    def placeTypes(self):
        return self.brain.getFeatureType

    def subject(self):
        return self.brain.Subject

    @export_config(json=False)
    def timePeriods(self):
        return self.brain.getTimePeriods

    @export_config(json=False)
    def temporalRange(self):
        # @@@ move to util function
        request = getRequest()
        if request is not None and hasattr(request, '_period_ranges'):
            period_ranges = request._period_ranges
        else:
            tp_vocab = get_vocabulary('time_periods')
            period_ranges = periodRanges(tp_vocab)
            if request is not None:
                request._period_ranges = period_ranges

        timePeriods = self.brain.getTimePeriods
        years = []
        for period in timePeriods:
            years.extend(list(period_ranges[period]))
        if len(years) >= 2:
            return min(years), max(years)
        else:
            return None

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
        filter = {'portal_type': 'Location'}
        for child in self.context.listFolderContents(filter):
            adapter = get_export_adapter(child)
            features.append(geojson.Feature(
                id=adapter.id(),
                properties=dict(
                    title=adapter.title(),
                    snippet=adapter._snippet(),
                    description=adapter.description(),
                    link=adapter.uri(),
                    location_precision=adapter.locationPrecision(),
                ),
                geometry=adapter.geometry(),
            ))
        return features

    def bbox(self):
        return self.brain.bbox or None

    @export_config(json=False)
    def extent(self):
        return self.brain.zgeo_geometry or None

    @export_config(json=False)
    def geoContext(self):
        note = self.brain.getModernLocation
        if not note:
            note = self.brain.Description
            match = re.search(r"cited: BAtlas (\d+) (\w+)", note)
            if match:
                note = "Barrington Atlas grid %s %s" % (
                    match.group(1), match.group(2).capitalize())
            else:
                note = ""
            note = unicode(note.replace(unichr(174), unichr(0x2194)))
            note = note.replace(unichr(0x2192), unichr(0x2194))
        return note
