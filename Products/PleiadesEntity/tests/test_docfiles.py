from Products.PleiadesEntity.tests.base import PleiadesEntityTestCase
from Testing import ZopeTestCase as ztc
import doctest
import unittest


optionflags = (
    doctest.ELLIPSIS
    | doctest.NORMALIZE_WHITESPACE
    | doctest.REPORT_ONLY_FIRST_FAILURE
    )


integration_tests = [
    'Entities.txt',
    'WSTransliteration.txt',
    'WSValidation.txt',
    'subscribers.txt',
    'LoadEntity.txt',
    # 'BatchLoad.txt',
    'attestations-view.txt',
    'citations.txt',
    'LoadCAP.txt'
]


def make_integration_suite(name):
    return ztc.ZopeDocFileSuite(
        name,
        package='Products.PleiadesEntity.tests',
        test_class=PleiadesEntityTestCase,
        optionflags=optionflags,
    )


def test_suite():
    return unittest.TestSuite(
        [make_integration_suite(n) for n in integration_tests]
    )
