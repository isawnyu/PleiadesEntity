request = container.REQUEST
RESPONSE =  request.RESPONSE

indexes = {
    "Language": 'getNameLanguage',
    "Completeness": 'getCompleteness',
    "Time Periods": 'getTimePeriods'
    }
vocabs = {
    "Language": 'ancient-name-languages',
    "Completeness": 'name-completeness',
    "Time Periods": 'time-periods'
    }

portalurl = context.portal_url()
portal = context.portal_url.getPortalObject()
vtool = context.portal_vocabularies
wftool = context.portal_workflow
catalog = context.portal_catalog

basequery = {'portal_type': 'Name', 'review_state': 'published'}

data = {}
sortedlabels = indexes.keys()
sortedlabels.sort()
data['sortedLabels'] = sortedlabels[:]

for label, index in indexes.items():

    vname = vocabs[label]
    values = catalog.uniqueValuesFor(index)
    vocab = {}
    values = vtool.restrictedTraverse(vname)
    for val in values:
        vocab[val['id']] = val['title']

    data[label] = []

    for v in values:
        query = basequery.copy()
        query[index] = v
        term = vocab.get(v, None)
        if term:
            tval = term
        else:
            tval = "Undefined"

        results = catalog(query)

        item = dict(
                    value=tval,
                    count=len(results),
                    details="%s/search?portal_type=Name&%s=%s" % (
                        portalurl, index, v)
                    )
        if len(results) <= 100:
            item['details'] = "%s/search?portal_type=Name&sort_on=sortable_title&%s=%s" % (portalurl, index, v)
        else:
            # subqueries using titleStarts index
            item['groups'] = []
            for group in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                chars = [char for char in group]
                query['titleStarts'] = chars
                results = catalog(query, sort_on='sortable_title')

                tqs = '&'.join(["titleStarts:list=%s" % char for char in chars])

                item['groups'].append(
                    dict(
                        value=group,
                        count=len(results),
                        details="%s/search?portal_type=Name&sort_on=sortable_title&%s=%s&%s" % (
                            portalurl, index, v, tqs)
                    ))

        data[label].append(item)
        data[label].sort(cmp=lambda x, y: cmp(x['value'], y['value']))

return data

