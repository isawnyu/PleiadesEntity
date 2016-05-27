from DateTime import DateTime
from datetime import datetime
from Products.PleiadesEntity.tests.base import PleiadesEntityTestCase
import csv
import json
import os
import shutil
import tempfile


class TestExport(PleiadesEntityTestCase):
    maxDiff = None

    def afterSetUp(self):
        fake_date = DateTime('2016-01-01')
        self.portal.portal_catalog.manage_catalogClear()
        self.setRoles(['Manager'])

        self.portal.REQUEST._period_ranges = {'roman': [-30, 300]}

        self.portal.invokeFactory('PlaceContainer', 'places')
        places = self.portal.places
        places.invokeFactory(
            'Place',
            id='1',
            title='Ninoe',
            description='This is a test.',
            creation_date=fake_date,
        )
        place = self.place = self.portal.places['1']
        self.portal.portal_workflow.doActionFor(place, 'publish')
        references = place.Schema()['referenceCitations']
        references.resize(0)

        # Create revision (with fake timestamp)
        import time
        _time = time.time
        time.time = lambda: int(fake_date)
        self.portal.portal_repository.save(place, comment='Initial Revision')
        time.time = _time

        nameAttested = u'\u039d\u03b9\u03bd\u1f79\u03b7'.encode('utf-8')
        nid = place.invokeFactory(
            'Name', 'ninoe',
            title='Ninoe',
            nameAttested=nameAttested,
            nameLanguage='grc',
            nameType='geographic',
            nameTransliterated='Ninoe',
            accuracy='accurate',
            completeness='complete',
            creation_date=fake_date,
        )
        attestations = place[nid].Schema()['attestations']
        attestations.resize(1)
        references = place[nid].Schema()['referenceCitations']
        references.resize(1)
        place[nid].update(
            attestations=[{
                'confidence': 'certain',
                'timePeriod': 'roman'
            }],
            referenceCitations=[{
                'identifier': 'http://books.google.com/books?id=Y10GAAAAQAAJ&pg=PA476',
                'range': 'StByz Ninoe',
                'type': 'citesAsEvidence',
            }],
        )
        self.portal.portal_workflow.doActionFor(place[nid], 'publish')

        place.invokeFactory(
            'Location', 'position',
            title='Point 1',
            geometry='Point:[-86.4808333333333, 34.769722222222]',
            creation_date=fake_date,
        )
        self.portal.portal_workflow.doActionFor(place.position, 'publish')

        places.invokeFactory(
            'Place',
            id='2',
        )
        place.addReference(places['2'], "connectsWith")
        self.portal.portal_workflow.doActionFor(places['2'], 'publish')

        place.setModificationDate(fake_date)
        self.portal.portal_catalog.catalog_object(place)
        place[nid].setModificationDate(fake_date)
        self.portal.portal_catalog.catalog_object(place[nid])
        place.position.setModificationDate(fake_date)
        self.portal.portal_catalog.catalog_object(place.position)

    def test_export_place(self):
        from ..browser.adapters.place import PlaceExportAdapter
        adapter = PlaceExportAdapter(self.place)

        self.assertEqual(adapter.uri(), 'http://nohost/plone/places/1')
        self.assertEqual(adapter.id(), '1')
        self.assertEqual(adapter.title(), 'Ninoe')
        self.assertEqual(adapter.description(), 'This is a test.')
        self.assertEqual(adapter.type(), 'FeatureCollection')

    def test_view_place_as_json(self):
        view = self.place.unrestrictedTraverse('@@newjson')
        response = view()
        expected = {
            '@type': 'Place',
            'uri': 'http://nohost/plone/places/1',
            'id': '1',
            'title': 'Ninoe',
            'description': 'This is a test.',
            'created': '2016-01-01T00:00:00Z',
            'review_state': 'published',
            'creators': [{
                u'uri': u'http://nohost/plone/author/test_user_1_',
                u'username': u'test_user_1_',
                u'homepage': None,
                u'name': u'',
            }],
            'contributors': [],
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'id': 'position',
                'properties': {
                    'title': 'Point 1',
                    'description': '',
                    'link': 'http://nohost/plone/places/1/position',
                    'snippet': 'Unknown',
                    'location_precision': 'precise',
                },
                'geometry': {
                    'coordinates': [-86.4808333333333, 34.769722222222],
                    'type': 'Point',
                }
            }],
            'reprPoint': [-86.4808333333333, 34.769722222222],
            'bbox': [-86.4808333333333, 34.769722222222,
                     -86.4808333333333, 34.769722222222],
            'connectsWith': ['http://pleiades.stoa.org/places/2'],
            'details': '',
            'placeTypes': ['unknown'],
            'provenance': 'Pleiades',
            'references': [],
            'rights': '',
            'subject': [],
            'locations': [{
                '@type': 'Location',
                'uri': 'http://nohost/plone/places/1/position',
                'id': 'position',
                'title': 'Point 1',
                'description': '',
                'created': '2016-01-01T00:00:00Z',
                'review_state': 'published',
                'history': [],
                'creators': [{
                    u'uri': u'http://nohost/plone/author/test_user_1_',
                    u'username': u'test_user_1_',
                    u'homepage': None,
                    u'name': u'',
                }],
                'contributors': [],
                'associationCertainty': 'certain',
                'accuracy': None,
                'featureType': ['unknown'],
                'geometry': {
                    'coordinates': [-86.4808333333333, 34.769722222222],
                    'type': 'Point',
                },
                'references': [],
                'attestations': [],
                'provenance': 'Pleiades',
                'details': '',
                'start': None,
                'end': None,
            }],
            'names': [{
                '@type': 'Name',
                'uri': 'http://nohost/plone/places/1/ninoe',
                'id': 'ninoe',
                'description': '',
                'created': '2016-01-01T00:00:00Z',
                'review_state': 'published',
                'history': [],
                'creators': [{
                    u'uri': u'http://nohost/plone/author/test_user_1_',
                    u'username': u'test_user_1_',
                    u'homepage': None,
                    u'name': u'',
                }],
                'contributors': [],
                'details': '',
                'associationCertainty': 'certain',
                'attestations': [{
                    'confidence': 'certain',
                    'timePeriod': 'roman',
                }],
                'attested': u'\u039d\u03b9\u03bd\u1f79\u03b7',
                'language': 'grc',
                'nameType': 'geographic',
                'romanized': 'Ninoe',
                'transcriptionAccuracy': 'accurate',
                'transcriptionCompleteness': 'complete',
                'references': [{
                    'uri': 'http://books.google.com/books?id=Y10GAAAAQAAJ&pg=PA476',
                    'shortCitation': 'StByz Ninoe',
                    'type': 'citesAsEvidence',
                }],
                'provenance': 'Pleiades',
                'history': [],
                'start': -30.0,
                'end': 300.0,
            }],
            'history': [{
                'comment': 'Initial Revision',
                'modified': '2016-01-01T00:00:00Z',
                'modifiedBy': 'test_user_1_',
            }]
        }
        actual = json.loads(response)
        del actual['@context']
        self.assertEqual(json.loads(json.dumps(expected)), actual)

    def test_csv_dump(self):
        from Products.PleiadesEntity.commands.dump import dump

        tmpdir = tempfile.mkdtemp()
        try:
            dump(self.app, tmpdir, ('csv-places',))
            filename = 'pleiades-places.csv'.format(datetime.now())
            filepath = os.path.join(tmpdir, 'dumps', filename)
            f = open(filepath, 'r')
            reader = csv.reader(f)
            columns = reader.next()
            row = reader.next()
            f.close()
        finally:
            shutil.rmtree(tmpdir)

        expectedColumns = [
            'authors',
            'bbox',
            'connectsWith',
            'created',
            'creators',
            'currentVersion',
            'description',
            'extent',
            'featureTypes',
            'geoContext',
            'hasConnectionsWith',
            'id',
            'locationPrecision',
            'maxDate',
            'minDate',
            'modified',
            'path',
            'reprLat',
            'reprLatLong',
            'reprLong',
            'tags',
            'timePeriods',
            'timePeriodsKeys',
            'timePeriodsRange',
            'title',
            'uid',
        ]
        self.assertEqual(expectedColumns, columns)

        expected = [
            "",
            "-86.4808333333, 34.7697222222, -86.4808333333, 34.7697222222",
            "2",
            "2016-01-01T00:00:00Z",
            "test_user_1_",
            "0",
            "This is a test.",
            '{"type": "Point", "coordinates": [-86.4808333333333, 34.769722222222]}',
            "unknown",
            "",
            "",
            "1",
            "precise",
            "300.0",
            "-30.0",
            "2016-01-01T00:00:00Z",
            "/places/1",
            "34.7697222222",
            "34.7697222222,-86.4808333333",
            "-86.4808333333",
            "",
            "R",
            "roman",
            "-30.0,300.0",
            "Ninoe",
        ]
        row.pop()  # remove uid, which is randomly generated
        self.assertEqual(expected, row)

    def test_csv_name_dump(self):
        from Products.PleiadesEntity.commands.dump import dump

        tmpdir = tempfile.mkdtemp()
        try:
            dump(self.app, tmpdir, ('csv-names',))
            filename = 'pleiades-names.csv'.format(datetime.now())
            filepath = os.path.join(tmpdir, 'dumps', filename)
            f = open(filepath, 'r')
            reader = csv.reader(f)
            columns = reader.next()
            row = reader.next()
            f.close()
        finally:
            shutil.rmtree(tmpdir)

        expectedColumns = [
            'authors',
            'bbox',
            'created',
            'creators',
            'currentVersion',
            'description',
            'extent',
            'id',
            'locationPrecision',
            'maxDate',
            'minDate',
            'modified',
            'nameAttested',
            'nameLanguage',
            'nameTransliterated',
            'path',
            'pid',
            'reprLat',
            'reprLatLong',
            'reprLong',
            'tags',
            'timePeriods',
            'timePeriodsKeys',
            'timePeriodsRange',
            'title',
            'uid',
        ]
        self.assertEqual(expectedColumns, columns)

        expected = [
            "",
            "-86.4808333333, 34.7697222222, -86.4808333333, 34.7697222222",
            "2016-01-01T00:00:00Z",
            "test_user_1_",
            "",
            "",
            '{"type": "Point", "coordinates": [-86.4808333333333, 34.769722222222]}',
            "ninoe",
            "precise",
            "300.0",
            "-30.0",
            "2016-01-01T00:00:00Z",
            u"\u039d\u03b9\u03bd\u1f79\u03b7".encode('utf-8'),
            "grc",
            "Ninoe",
            "/places/1/ninoe",
            "/places/1",
            "34.7697222222",
            "34.7697222222,-86.4808333333",
            "-86.4808333333",
            "",
            "R",
            "roman",
            "-30.0,300.0",
            "Ninoe",
        ]
        row.pop()  # remove uid, which is randomly generated
        self.assertEqual(expected, row)

    def test_csv_location_dump(self):
        from Products.PleiadesEntity.commands.dump import dump

        tmpdir = tempfile.mkdtemp()
        try:
            dump(self.app, tmpdir, ('csv-locations',))
            filename = 'pleiades-locations.csv'.format(datetime.now())
            filepath = os.path.join(tmpdir, 'dumps', filename)
            f = open(filepath, 'r')
            reader = csv.reader(f)
            columns = reader.next()
            row = reader.next()
            f.close()
        finally:
            shutil.rmtree(tmpdir)

        expectedColumns = [
            'authors',
            'bbox',
            'created',
            'creators',
            'currentVersion',
            'description',
            'featureType',
            'geometry',
            'id',
            'locationPrecision',
            'maxDate',
            'minDate',
            'modified',
            'path',
            'pid',
            'reprLat',
            'reprLatLong',
            'reprLong',
            'tags',
            'timePeriods',
            'timePeriodsKeys',
            'timePeriodsRange',
            'title',
            'uid',
        ]
        self.assertEqual(expectedColumns, columns)

        expected = [
            "",
            "-86.4808333333, 34.7697222222, -86.4808333333, 34.7697222222",
            "2016-01-01T00:00:00Z",
            "test_user_1_",
            "",
            "",
            "unknown",
            '{"type": "Point", "coordinates": [-86.4808333333333, 34.769722222222]}',
            "position",
            "precise",
            "",
            "",
            "2016-01-01T00:00:00Z",
            "/places/1/position",
            "/places/1",
            "34.7697222222",
            "34.7697222222,-86.4808333333",
            "-86.4808333333",
            "",
            "",
            "",
            "",
            "Point 1",
        ]
        row.pop()  # remove uid, which is randomly generated
        self.assertEqual(expected, row)
