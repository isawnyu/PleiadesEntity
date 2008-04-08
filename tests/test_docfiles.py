import os, sys

import glob
import unittest
import doctest
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup, PloneSite, ZCMLLayer
import _testing

ptc.installProduct('Geographer')
ptc.installProduct('ATVocabularyManager')
ptc.installProduct('PleiadesEntity')
ptc.setupPloneSite(products=['Archetypes', 'ATVocabularyManager', 'Geographer', 'PleiadesEntity'])

optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE # | doctest.REPORT_ONLY_FIRST_FAILURE

class PleiadesEntityTestCase(ptc.PloneTestCase):

    layer = PloneSite

    def afterSetUp(self):
        self.test_params = _testing
        
        lpf = self.portal.portal_types['Large Plone Folder']
        lpf_allow = lpf.global_allow
        lpf.global_allow = True

        n = self.portal.portal_types['Name']
        n_allow = n.global_allow
        n.global_allow = True

        # Currently this stuff isn't being torn down between doctests. Why not?
        try:
            self.folder.invokeFactory('Large Plone Folder', id='names')
            self.folder['names'].invokeFactory('Large Plone Folder',id='duplicates')
            self.folder.invokeFactory('LocationContainer', id='locations')
            self.folder.invokeFactory('PlaceContainer', id='places')
        except:
            pass

integration_tests = [
    'Entities.txt',
    'Names.txt',
    'TemporalAttestations.txt',
    'Vocabularies.txt',
    'WSTransliteration.txt',
    'WSValidation.txt',
    'LoadEntity.txt',
    'BatchLoad.txt'
    ]

functional_tests = [
    'LocationViews.txt',
    'NameViews.txt'
    ]

def make_integration_suite(name):
    return ztc.ZopeDocFileSuite(
                name,
                package='Products.PleiadesEntity.tests',
                test_class=PleiadesEntityTestCase,
                optionflags=optionflags,
                )

def make_functional_suite(name):
    return ztc.FunctionalDocFileSuite(
                name,
                package='Products.PleiadesEntity.tests',
                test_class=PleiadesEntityTestCase,
                optionflags=optionflags,
                )

def test_suite():
    return unittest.TestSuite(
        [make_integration_suite(n) for n in integration_tests] 
      + [make_functional_suite(n) for n in functional_tests]
      )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

