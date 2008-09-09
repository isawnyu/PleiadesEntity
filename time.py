from Products.CMFCore.utils import getToolByName


class TimePeriodCmp(object):

    def __init__(self, context):
        self.vtool = getToolByName(context, 'portal_vocabularies')
        vt = self.vtool.getVocabularyByName('time-periods')
        self.t_keys = vt.getDisplayList(vt).keys()
        self.t_vals = vt.getDisplayList(vt).values()

    def __call__(self, a, b):
        if a in self.t_keys:
            ai = self.t_keys.index(a)
        elif a in self.t_vals:
            ai = self.t_vals.index(a)
        else:
            # a value not in the vocab is greater
            return 1
        if b in self.t_keys:
            bi = self.t_keys.index(b)
        elif b in self.t_vals:
            bi = self.t_vals.index(b)
        else:
            # a value not in the vocab is greater
            return -1

        return ai - bi
