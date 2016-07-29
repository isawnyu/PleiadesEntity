import logging

from Acquisition import aq_parent

from plone.indexer.decorator import indexer
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName

from pleiades.transliteration import transliterate_name
from Products.PleiadesEntity.content.interfaces import IName, IPlace

log = logging.getLogger('PleiadesEntity')

@indexer(IName)
def name_titleStarts(obj, **kw):
    title = obj.getNameTransliterated() or obj.Title()
    if not title:
        nameAttested = obj.getNameAttested()
        nameLanguage = obj.getNameLanguage()
        if not nameAttested or not nameLanguage:
            return None
        title = transliterate_name(nameLanguage, nameAttested)
    if len(title) > 0:
        return title[0].upper()
    else:
        return None

@indexer(IPlace)
def place_titleStarts(obj, **kw):
    tvalue = obj.Title() or "?"
    return tvalue[0].upper()

@indexer(IContentish)
def currentVersion(obj, **kw):
    repo = getToolByName(obj, 'portal_repository')
    rt = repo.getHistoryMetadata(obj)
    return rt.getVersionId(None, False)

@indexer(IPlace)
def connectsWith(obj, **kw):
    return [o.getConnection().getId() for o in obj.getSubConnections()] or None

@indexer(IPlace)
def hasConnectionsWith(obj, **kw):
    return [aq_parent(o).getId() for o in obj.getReverseConnections()] or None
