import logging

from plone.indexer.decorator import indexer

from pleiades.transliteration import transliterate_name
from Products.PleiadesEntity.content.interfaces import IName, IPlace

log = logging.getLogger('PleiadesEntity')

@indexer(IName)
def name_titleStarts(object, **kw):
    title = object.getNameTransliterated() or object.Title()
    if not title:
        nameAttested = object.getNameAttested()
        nameLanguage = object.getNameLanguage()
        if not nameAttested or not nameLanguage:
            return None
        title = transliterate_name(nameLanguage, nameAttested)
    if len(title) > 0:
        return title[0].upper()
    else:
        return None

@indexer(IPlace)
def place_titleStarts(object, **kw):
    tvalue = object.Title() or "?"
    return tvalue[0].upper()

