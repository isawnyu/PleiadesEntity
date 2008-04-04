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

#REQUIRE_TESTBROWSER = ['PublishGeoEntity.txt']

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
        #ztc.FunctionalDocFileSuite(
        #    'browser.txt',
        #    package='Products.Geographer.tests',
        #    test_class=ptc.FunctionalTestCase,
        #    optionflags=optionflags,
        #    )
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


#def list_doctests():
#    return [filename for filename in
#            glob.glob(os.path.sep.join([TEST_HOME, '*.txt']))]

#d#ef list_nontestbrowser_tests():
#    return [filename for filename in list_doctests()
#            if os.path.basename(filename) not in REQUIRE_TESTBROWSER]

#def test_suite():
# 
#    # BBB: We can obviously remove this when testbrowser is Plone
#    #      mainstream, read: with Five 1.4.
#    try:
#        import Products.Five.testbrowser
#    except ImportError:
#        print >> sys.stderr, ("WARNING: testbrowser not found - you probably"
#                              "need to add Five 1.4 to the Products folder. "
#                              "testbrowser tests skipped")
#        from Products.Five import zcml
#        from Products import PleiadesEntity
#        zcml.load_config('configure.zcml', package=PleiadesEntity)
#        filenames = list_nontestbrowser_tests()
#    else:
#        filenames = list_doctests()
#
#    return unittest.TestSuite(
#        [Suite(os.path.basename(filename),
#               optionflags=OPTIONFLAGS,
#               package=TEST_PACKAGE,
#               globs=_testing.__dict__,
#               test_class=PloneTestCase.FunctionalTestCase)
#         for filename in filenames]
#        )
