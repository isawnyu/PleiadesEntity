from Products.PleiadesEntity.tests.base import PleiadesEntityTestCase
import json


class TestExport(PleiadesEntityTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('PlaceContainer', 'places')
        self.portal.places.invokeFactory(
            'Place',
            id='1',
            title='Atlantis',
            description='This is a test.',
        )
        self.place = self.portal.places['1']

    def test_export_place(self):
        from Products.PleiadesEntity.browser.adapters.place import PlaceExportAdapter
        adapter = PlaceExportAdapter(self.place)

        self.assertEqual(adapter.uri(), 'http://nohost/plone/places/1')
        self.assertEqual(adapter.id(), '1')
        self.assertEqual(adapter.title(), 'Atlantis')
        self.assertEqual(adapter.description(), 'This is a test.')

    def test_view_place_as_json(self):
        view = self.place.unrestrictedTraverse('@@json')
        response = view()
        self.assertEqual(json.loads(response), {
            'uri': 'http://nohost/plone/places/1',
            'id': '1',
            'title': 'Atlantis',
            'description': 'This is a test.',
        })
