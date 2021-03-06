## Script (Python) "getBackRefContents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=refs,b_size=50
##title=wrapper method around to use catalog to get folder contents
##

from AccessControl import Unauthorized

contents = []
for b in refs:
    try:
        contents.append(b.getSourceObject())
    except Unauthorized:
        pass

from Products.CMFPlone import Batch
b_start = context.REQUEST.get('b_start', 0)
batch = Batch(contents, b_size, int(b_start), orphan=0)
return batch

