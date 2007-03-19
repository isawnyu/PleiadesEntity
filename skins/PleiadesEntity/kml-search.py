## Script (Python) "kml-search"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=q
##title=
##
pid = container.getBaIdent(q)
response = container.REQUEST.RESPONSE
response.setStatus(301)
response.redirect("http://pleiades.stoa.org/places/%s/kml" % pid)
