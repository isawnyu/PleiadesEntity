import os, sys

import glob
import unittest
import doctest
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup, PloneSite
import _testing

ptc.installProduct('Geographer')
ptc.installProduct('ATVocabularyManager')
ptc.installProduct('PleiadesEntity')
ptc.setupPloneSite(products=['Archetypes', 'ATVocabularyManager', 'Geographer', 'PleiadesEntity'])

optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE

class PleiadesEntityTestCase(ptc.PloneTestCase):

    def afterSetUp(self):
        self.test_params = _testing


def test_suite():
    return unittest.TestSuite([
        ztc.ZopeDocFileSuite(
            'Entities.txt',
            package='Products.PleiadesEntity.tests',
            test_class=PleiadesEntityTestCase,
            optionflags=optionflags,
            ),
        ztc.ZopeDocFileSuite(
            'LoadEntity.txt',
            package='Products.PleiadesEntity.tests',
            test_class=PleiadesEntityTestCase,
            optionflags=optionflags,
            ),
        ztc.ZopeDocFileSuite(
            'BatchLoad.txt',
            package='Products.PleiadesEntity.tests',
            test_class=PleiadesEntityTestCase,
            optionflags=optionflags,
            ),
        ztc.FunctionalDocFileSuite(
            'LocationViews.txt',
            package='Products.PleiadesEntity.tests',
            test_class=PleiadesEntityTestCase,
            optionflags=optionflags,
            ),
        ztc.FunctionalDocFileSuite(
            'NameViews.txt',
            package='Products.PleiadesEntity.tests',
            test_class=PleiadesEntityTestCase,
            optionflags=optionflags,
            ),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
