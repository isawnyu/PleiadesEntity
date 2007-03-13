import os, sys

import glob
import doctest
import unittest
from Globals import package_home
from Products.PloneTestCase import PloneTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

import _testing
from _testing import *

PloneTestCase.installProduct('PleiadesGeocoder')
PloneTestCase.installProduct('PleiadesOpenLayers')
PloneTestCase.installProduct('ATVocabularyManager')
PloneTestCase.installProduct(PRODUCT_NAME)
PloneTestCase.setupPloneSite(products=['ATVocabularyManager', 'PleiadesGeocoder', PRODUCT_NAME])

REQUIRE_TESTBROWSER = ['PublishGeoEntity.txt']

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def list_doctests():
    return [filename for filename in
            glob.glob(os.path.sep.join([TEST_HOME, '*.txt']))]

def list_nontestbrowser_tests():
    return [filename for filename in list_doctests()
            if os.path.basename(filename) not in REQUIRE_TESTBROWSER]

def test_suite():
 
    # BBB: We can obviously remove this when testbrowser is Plone
    #      mainstream, read: with Five 1.4.
    try:
        import Products.Five.testbrowser
    except ImportError:
        print >> sys.stderr, ("WARNING: testbrowser not found - you probably"
                              "need to add Five 1.4 to the Products folder. "
                              "testbrowser tests skipped")
        from Products.Five import zcml
        from Products import PleiadesEntity
        zcml.load_config('configure.zcml', package=PleiadesEntity)
        filenames = list_nontestbrowser_tests()
    else:
        filenames = list_doctests()

    return unittest.TestSuite(
        [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package=TEST_PACKAGE,
               globs=_testing.__dict__,
               test_class=PloneTestCase.FunctionalTestCase)
         for filename in filenames]
        )
