import logging

from plone.indexer.decorator import indexer
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName

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

@indexer(IContentish)
def currentVersion(obj, **kw):
    repo = getToolByName(obj, 'portal_repository')
    rt = repo.getHistoryMetadata(obj)
    return rt.getVersionId(None, False)

@indexer(IPlace)
def connectsWith(obj, **kw):
    return [o.getId() for o in obj.getRefs("connectsWith")] or None

@indexer(IPlace)
def hasConnectionsWith(obj, **kw):
    return [o.getId() for o in obj.getBRefs("connectsWith")] or None

