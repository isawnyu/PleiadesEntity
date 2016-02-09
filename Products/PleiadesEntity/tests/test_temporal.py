import unittest

from zgeo.geographer.interfaces import IGeoreferenced
from zope.interface import implements

from Products.PleiadesEntity.content import Temporal, Place, Location, Name
from Products.PleiadesEntity.time import periodRanges, temporal_overlap


class Term:
    def __init__(self, key, value, description):
        self.key = key
        self.value = value
        self.description = description
    def getId(self):
        return self.key
    def Title(self):
        return self.value
    def Description(self):
        return self.description
    def getTermKey(self):
        return self.key
    def getTermValue(self):
        return self.value

VOCAB = {'hellenistic-republican': Term(
    'hellenistic-republican', 
    "Hellenistic Greek, Roman Republic (330 BC-30 BC)", 
    "The Hellenistic period in Greek history and the middle-to-late Republican period in Roman history. For the purposes of Pleiades, this period is said to begin in the year 330 and end in the year 30 before the birth of Christ. [[-330, -30]]"
    ), 'roman': Term(
    'roman', 
    "Roman, early Empire (30 BC-AD 300)", 
    "The Roman period (i.e., the early Roman Empire) in Greek and Roman history. For the purposes of Pleiades, this period is said to begin in the year 30 before the birth of Christ and to end in the year 300 after the birth of Christ. [[-30, 300]]"
    ), 'late-antique': Term(
    'late-antique', 
    "Late Antique (AD 300-AD 640)", 
    "The Late Antique period in Greek and Roman history. For the purposes of Pleiades, this period is said to begin in the year 300 and to end in the year 640 after the birth of Christ. [[300, 640]]"
    )}

class MockTemporalContent(Temporal.Temporal):
    def __init__(self, attestations):
        self.attestations = attestations
        self.aq_parent = None
    def getAttestations(self):
        return self.attestations

class MockPreciseLocation(MockTemporalContent):
    implements(IGeoreferenced)
    def __init__(self, attestations):
        self.attestations = attestations
    def getAttestations(self):
        return self.attestations
    __geo_interface__ = {'type': "Point", 'coordinates': [0.0, 0.0]}
    bounds = (0.0, 0.0, 0.0, 0.0)
    type = 'Point'
    coordinates = [0.0, 0.0]
    precision = 'precise'
    crs = None

class MockPlace(object):
    locations = []
    def getLocations(self):
        return self.locations

class PeriodsTestCase(unittest.TestCase):
    def test_ranges(self):
        ranges = periodRanges(VOCAB)
        items = sorted(ranges.items())
        self.failUnlessEqual(
            items, [
                ('hellenistic-republican', (-330.0, -30.0)), 
                ('late-antique', (300.0, 640.0)), 
                ('roman', (-30.0, 300.0))
                ])

class TemporalMixinTestCase(unittest.TestCase):
    def test_range(self):
        class MockTemporalContent(Temporal.Temporal):
            def getAttestations(self):
                return [
                    {'timePeriod': 'hellenistic-republican', 'confidence': 'confident'},
                    {'timePeriod': 'roman', 'confidence': 'confident'}]
        mock = MockTemporalContent()
        self.failUnlessEqual(mock.temporalRange(VOCAB), (-330.0, 300.0))

class TemporalOverlapTestCase(unittest.TestCase):
    def test_nonoverlap(self):
        p = MockTemporalContent([{'timePeriod': 'hellenistic-republican'}])
        q = MockTemporalContent([{'timePeriod': 'roman'}])
        self.failIf(temporal_overlap(p, q, VOCAB))
    def test_overlap(self):
        p = MockTemporalContent([{'timePeriod': 'roman'}])
        q = MockTemporalContent([{'timePeriod': 'roman'}])
        self.failUnless(temporal_overlap(p, q, VOCAB))

def test_suite():
    loads = unittest.defaultTestLoader.loadTestsFromTestCase
    suite = unittest.TestSuite()
    suite.addTests(loads(PeriodsTestCase))
    suite.addTests(loads(TemporalMixinTestCase))
    suite.addTests(loads(TemporalOverlapTestCase))
    return suite

