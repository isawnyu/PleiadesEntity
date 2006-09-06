from urllib import quote

def cookZopeID(rawID):
    cookedID = rawID.expandtabs(1)
    cookedID = cookedID.replace(' ','')
    cookedID = cookedID.lower()
    cookedID = quote(cookedID)
    cookedID = cookedID.encode('ascii', 'ignore')
    return cookedID
