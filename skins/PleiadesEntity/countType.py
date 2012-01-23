## Script (Python) "countType"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
def group(number):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    groups.reverse()
    return s + ','.join(groups)

catalog = container.portal_catalog
num_places = len(catalog.searchResults(
    {'portal_type': 'Place', 'review_state': 'published'}) )
num_names = len(catalog.searchResults(
    {'portal_type': 'Name', 'review_state': 'published'}) )
num_locations = len(catalog.searchResults(
    {'portal_type': 'Location', 'review_state': 'published'}) )
return {
    "num_places": group(num_places), 
    "num_names": group(num_names), 
    "num_locations": group(num_locations) }

