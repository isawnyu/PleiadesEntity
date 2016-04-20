from DateTime import DateTime
from Products.PleiadesEntity.tests.base import PleiadesEntityTestCase
import json


class TestExport(PleiadesEntityTestCase):
    maxDiff = None

    def afterSetUp(self):
        fake_date = DateTime('2016-01-01')
        self.setRoles(['Manager'])
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

        place.invokeFactory(
            'Location', 'position',
            title='Point 1',
            geometry='Point:[-86.4808333333333, 34.769722222222]',
            creation_date=DateTime('2016-01-01'),
        )
        self.portal.portal_workflow.doActionFor(place.position, 'publish')

        places.invokeFactory(
            'Place',
            id='2',
        )
        place.addReference(places['2'], "connectsWith")

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
            'uri': 'http://nohost/plone/places/1',
            'id': '1',
            'title': 'Ninoe',
            'description': 'This is a test.',
            'created': '2016-01-01T00:00:00',
            'review_state': 'private',
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
            'connectsWith': ['http://nohost/plone/places/2'],
            'details': '',
            'placeTypes': ['unknown'],
            'provenance': 'Pleiades',
            'references': [],
            'rights': '',
            'subject': [],
            'locations': [{
                'uri': 'http://nohost/plone/places/1/position',
                'id': 'position',
                'title': 'Point 1',
                'description': '',
                'created': '2016-01-01T00:00:00',
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
            }],
            'names': [{
                'uri': 'http://nohost/plone/places/1/ninoe',
                'id': 'ninoe',
                'description': '',
                'created': '2016-01-01T00:00:00',
                'review_state': 'private',
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
            }],
            'history': [{
                'comment': 'Initial Revision',
                'modified': '2016-01-01T00:00:00',
                'modifiedBy': 'test_user_1_',
            }]
        }
        self.assertEqual(json.loads(response), json.loads(json.dumps(expected)))
