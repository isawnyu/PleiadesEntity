import os, sys

import glob
import doctest
import unittest
from Globals import package_home
from Products.PloneTestCase import PloneTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

# Shouldn't be necessary with latest SVN PTC
#from Products.Five import zcml
#import Products
#zcml.load_config('configure.zcml', package=Products.PleiadesGeocoder)

PRODUCT_NAME = 'GeographicEntityLite'
TEST_PACKAGE = "Products/%s/tests" % PRODUCT_NAME

PloneTestCase.installProduct(PRODUCT_NAME)
PloneTestCase.setupPloneSite(products=[PRODUCT_NAME])


REQUIRE_TESTBROWSER = ['PublishGeoEntity.txt']

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def list_doctests():
    home = os.path.sep.join([os.environ['SOFTWARE_HOME'], 'Products',
        PRODUCT_NAME])
    return [filename for filename in
            glob.glob(os.path.sep.join([home, 'tests', '*.txt']))]

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
        filenames = list_nontestbrowser_tests()
    else:
        filenames = list_doctests()

    return unittest.TestSuite(
        [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package=TEST_PACKAGE,
               test_class=PloneTestCase.FunctionalTestCase)
         for filename in filenames]
        )

