from plone.indexer.decorator import indexer

from Products.PleiadesEntity.content.interfaces import IName


@indexer(IName)
def name_titleStarts(object, **kw):
    return (object.getNameTransliterated() or object.Title())[0].upper()

