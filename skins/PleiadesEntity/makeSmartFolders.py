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
        
try:
    smart_folder_tool.addIndex('getPlaceType', 'Place Type', 'Type of ancient place', enabled=True)
except:
    pass
try:
    smart_folder_tool.addIndex('getTimePeriods', 'Time Periods', 'Attested time periods', enabled=True)
except:
    pass

#v_types = container.portal_catalog.uniqueValuesFor('getPlaceType')
#v_times = container.portal_catalog.uniqueValuesFor('getTimePeriods')
utils = container.plone_utils

vocab_time = container.portal_vocabularies.getVocabularyByName('time-periods')
vocab_type = container.portal_vocabularies.getVocabularyByName('place-types')

v_types = [v.getTermKey() for k,v in vocab_type.items() if k.startswith('term')]
v_times = [v.getTermKey() for k,v in vocab_time.items() if k.startswith('term')]

# [time]/[type]
for v in v_times:
    id = context.invokeFactory('Topic', id=utils.normalizeString(v),
        title=vocab_time.getTermByKey(key=v).getTermValue().capitalize())
    topic = getattr(context, id)
    c = topic.addCriterion('getTimePeriods', 'ATSimpleStringCriterion')
    c.setValue(v)
    c = topic.addCriterion('Type', 'ATPortalTypeCriterion')
    c.setValue('Place')
    topic.setSortCriterion('sortable_title', reversed=False)

    for t in v_types:
        sid = topic.invokeFactory('Topic', id=utils.normalizeString(t),
               title=vocab_type.getTermByKey(key=t).getTermValue().capitalize())
        subtopic = getattr(topic, sid)
        subtopic.setAcquireCriteria(True)
        c = subtopic.addCriterion('getPlaceType', 'ATSimpleStringCriterion')
        c.setValue(t)
        subtopic.setSortCriterion('sortable_title', reversed=False)

# [type]/[time]
for t in v_types:
    id = context.invokeFactory('Topic', id=utils.normalizeString(t),
        title=vocab_type.getTermByKey(key=t).getTermValue().capitalize())
    topic = getattr(context, id)
    c = topic.addCriterion('getPlaceType', 'ATSimpleStringCriterion')
    c.setValue(t)
    c = topic.addCriterion('Type', 'ATPortalTypeCriterion')
    c.setValue('Place')
    topic.setSortCriterion('sortable_title', reversed=False)

    for v in v_times:
        sid = topic.invokeFactory('Topic', id=utils.normalizeString(v),
               title=vocab_time.getTermByKey(key=v).getTermValue().capitalize())
        subtopic = getattr(topic, sid)
        subtopic.setAcquireCriteria(True)
        c = subtopic.addCriterion('getTimePeriods', 'ATSimpleStringCriterion')
        c.setValue(v)
        topic.setSortCriterion('sortable_title', reversed=False)

