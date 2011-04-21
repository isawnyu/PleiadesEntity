from plone.indexer.decorator import indexer

from Products.PleiadesEntity.content.interfaces import IName


@indexer(IName)
def name_titleStarts(object, **kw):
    tvalue = object.getNameTransliterated() or object.Title() or "?"
    return tvalue[0].upper()

