from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup, PloneSite
from Testing import ZopeTestCase as ztc
import os

ztc.installProduct('Products.ATBackRef')
ztc.installProduct('Products.CompoundField')
ztc.installProduct('Products.OrderableReferenceField')
ztc.installProduct('pleiades.vocabularies')
ztc.installProduct('PleiadesEntity')


@onsetup
def setup_pleiades_entity():
    fiveconfigure.debug_mode = True
    import Products.PleiadesEntity
    zcml.load_config('configure.zcml', Products.PleiadesEntity)
    fiveconfigure.debug_mode = False

    ztc.installPackage('pleiades.vocabularies')
    ztc.installPackage('Products.PleiadesEntity')

setup_pleiades_entity()
ptc.setupPloneSite(products=['PleiadesEntity'])


class PleiadesEntityTestCase(ptc.PloneTestCase):
    layer = PloneSite

    def afterSetUp(self):
        self.TEST_DATA = os.path.join(
            os.path.dirname(__file__), 'data'
            )
        # Currently this stuff isn't being torn down between doctests. Why not?
        try:
            self.folder.invokeFactory('FeatureContainer', id='features')
            self.folder['features'].invokeFactory('Folder', id='metadata')
            self.folder.invokeFactory('PlaceContainer', id='places')
            mid = self.folder['features']['metadata'].invokeFactory(
                'PositionalAccuracy', id='cap-map65')
            self.folder['features']['metadata'][mid].setValue(0.01)
            self.folder['features']['metadata'][mid].setText(
                "That's right, 1 cm!")
        except:
            pass

    def runTest(self):
        return