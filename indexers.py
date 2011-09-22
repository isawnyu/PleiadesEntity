from plone.indexer.decorator import indexer

from Products.PleiadesEntity.content.interfaces import IName, IPlace


@indexer(IName)
def name_titleStarts(object, **kw):
    tvalue = object.getNameTransliterated() or object.Title() or "?"
    return tvalue[0].upper()

@indexer(IPlace)
def place_titleStarts(object, **kw):
    tvalue = object.Title() or "?"
    return tvalue[0].upper()

