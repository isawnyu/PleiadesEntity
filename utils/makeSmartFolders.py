v_types = container.portal_catalog.uniqueValuesFor('placeType')
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

    for t in v_types:
        sid = topic.invokeFactory('Topic', id=utils.normalizeString(t), title=t)
        subtopic = getattr(topic, sid)
        subtopic.setAcquireCriteria(True)
        c = subtopic.addCriterion('placeType', 'ATSelectionCriterion')
        c.setValue([t])

# [type]/[time]
for t in v_types:
    id = context.invokeFactory('Topic', id=utils.normalizeString(t), title=t)
    topic = getattr(context, id)
    c = subtopic.addCriterion('placeType', 'ATSelectionCriterion')
    c.setValue([t])
    c = topic.addCriterion('Type', 'ATPortalTypeCriterion')
    c.setValue('Ancient Place')

    for v in v_times:
        sid = topic.invokeFactory('Topic', id=utils.normalizeString(v), title=v)
        subtopic = getattr(topic, sid)
        subtopic.setAcquireCriteria(True)
        c = topic.addCriterion('getTimePeriods', 'ATSelectionCriterion')
        c.setValue([v])

