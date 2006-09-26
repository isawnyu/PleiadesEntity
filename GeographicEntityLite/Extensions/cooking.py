from urllib import quote
import transaction

from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName

def cookZopeID(rawID):
    cookedID = rawID.expandtabs(1)
    cookedID = cookedID.replace(' ','')
    cookedID = cookedID.lower()
    cookedID = quote(cookedID)
    cookedID = cookedID.encode('ascii', 'ignore')
    return cookedID
    
def setIdFromTitle(obj):
    
    # get the oldID, to prevent needless thrashing later
    oldID = obj.getId()
    
    # is there a title for this object? if not, fail
    title = obj.Title()
    if not title:
        return None
        
    # is the plone tool available, and does it have the function usually used to
    # normalize strings for id cooking? if not, fail
    ptool = getToolByName(obj, 'plone_utils', None)
    if ptool is None or not shasattr(ptool, 'normalizeString'):
        return None
        
    # use plone tool to normalize title, hopefully (gently) removing anything that
    # would produce an illegal url
    newID = ptool.normalizeString(title)
    
    # if this would result in no effective change, do nothing further
    if oldID == newID:
        return oldID
    
    # check id, if possible, and make sure it is unique
    check_id = getattr(obj, 'check_id', None)
    if check_id is None or check_id(newID, required=1):
        newID = makeIDUnique(obj, newID)
        
    # set the id
    transaction.savepoint(optimistic=True)
    obj.setId(newID)
    return newID
    
def setGeoTitleFromNames(obj):
    # get old title
    oldTitle = obj.Title()

    newTitle = ''    
    names = obj.listFolderContents()
    if len(names) == 0:
        enType = obj.getGeoEntityType()
        newTitle = 'Unnamed ' + enType
        enModLoc = obj.getModernLocation()
        if enModLoc != '':
            newTitle += ', modern location: ' + enModLoc
    else:
        try: 
            initNameType  = names[0].getGeoNameType()
        except:
            pass
        else:
            renames = []
            for name in names:
                if name.getGeoNameType() == initNameType:
                    renames.append(name)
            for i, name in enumerate(renames):
                if i > 0:
                    newTitle += '/'
                newTitle += name.Title()
                
    if newTitle != '':
        obj.setTitle(newTitle)

    return newTitle
    
def makeIDUnique(obj, newID):
    uniqueID = obj._findUniqueId(newID)
    return uniqueID
