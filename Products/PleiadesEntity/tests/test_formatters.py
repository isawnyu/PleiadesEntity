import unittest


class TestJsonFormatter(unittest.TestCase):

    def test_json_formatter(self):

        class MockExportAdapter(object):
            def id(self):
                return 'foo'

        from Products.PleiadesEntity.browser.formatters.as_json import format_json
        adapter = MockExportAdapter()
        json = format_json(adapter)
        self.assertEqual(json, '{"id": "foo"}')
