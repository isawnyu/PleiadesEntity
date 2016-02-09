import re
from Products.CMFCore.utils import getToolByName


class TimePeriodCmp(object):

    def __init__(self, context):
        self.vtool = getToolByName(context, 'portal_vocabularies')
        vt = self.vtool.getVocabularyByName('time-periods')
        self.t_keys = vt.getDisplayList(vt).keys()

    def __call__(self, a, b):
        if a in self.t_keys:
            ai = self.t_keys.index(a)
        else:
            # a value not in the vocab is greater
            return 1
        if b in self.t_keys:
            bi = self.t_keys.index(b)
        else:
            # a value not in the vocab is greater
            return -1
        return ai - bi

def periodRanges(vocab):
    """Compute a dict of ranges from the Pleiades time period vocabulary"""
    ranges = {}
    for key, term in vocab.items():
        descr = term.Description()
        m = re.search(
            r"\[\[(-{0,1}\d*\.{0,1}\d*)\s*,\s*(-{0,1}\d*\.{0,1}\d*)\]\]", 
            descr)
        if m is not None:
            min = float(m.group(1))
            max = float(m.group(2))
            ranges[term.getTermKey()] = min, max
    return ranges

def temporal_overlap(a, b, period_vocab=None):
    """Compare two Temporal objects"""
    ra = a.temporalRange(period_vocab)
    rb = b.temporalRange(period_vocab)
    if not ra or not rb:
        return False
    else:
        amin, amax = ra
        bmin, bmax = rb
        return amin < bmax and amax > bmin or amin == bmin and amax == bmax

def to_ad(year):
    sign = (year>0)*2-1
    if sign >= 0:
        return "AD %d" % year
    else:
        return "%d BC" % (sign*year)

