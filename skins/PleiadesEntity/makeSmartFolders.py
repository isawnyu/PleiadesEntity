## Script (Python) "makeSmartFolders"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

smart_folder_tool = container.portal_atct
        
try:
    smart_folder_tool.removeIndex("getPlaceType")
except:
    pass
        
try:
    smart_folder_tool.removeIndex("getTimePeriods")
except:
    pass
        
smart_folder_tool.addIndex('getPlaceType', 'Place Type', 'Type of ancient place', enabled=True)
smart_folder_tool.addIndex('getTimePeriods', 'Time Periods', 'Attested time periods', enabled=True)

v_types = container.portal_catalog.uniqueValuesFor('getPlaceType')
v_times = container.portal_catalog.uniqueValuesFor('getTimePeriods')
utils = container.plone_utils

# [time]/[type]
for v in v_times:
    id = context.invokeFactory('Topic', id=utils.normalizeString(v), title=v)
    topic = getattr(context, id)
    c = topic.addCriterion('getTimePeriods', 'ATSelectionCriterion')
    c.setValue([v])
    c = topic.addCriterion('Type', 'ATPortalTypeCriterion')
    c.setValue('Ancient Place')
    topic.setSortCriterion('sortable_title', reversed=False)

    for t in v_types:
        sid = topic.invokeFactory('Topic', id=utils.normalizeString(t), title=t)
        subtopic = getattr(topic, sid)
        subtopic.setAcquireCriteria(True)
        c = subtopic.addCriterion('getPlaceType', 'ATSelectionCriterion')
        c.setValue([t])
        subtopic.setSortCriterion('sortable_title', reversed=False)

# [type]/[time]
for t in v_types:
    id = context.invokeFactory('Topic', id=utils.normalizeString(t), title=t)
    topic = getattr(context, id)
    c = topic.addCriterion('getPlaceType', 'ATSelectionCriterion')
    c.setValue([t])
    c = topic.addCriterion('Type', 'ATPortalTypeCriterion')
    c.setValue('Ancient Place')
    topic.setSortCriterion('sortable_title', reversed=False)

    for v in v_times:
        sid = topic.invokeFactory('Topic', id=utils.normalizeString(v), title=v)
        subtopic = getattr(topic, sid)
        subtopic.setAcquireCriteria(True)
        c = subtopic.addCriterion('getTimePeriods', 'ATSelectionCriterion')
        c.setValue([v])
        topic.setSortCriterion('sortable_title', reversed=False)

