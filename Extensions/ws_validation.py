from pleiades.transliteration import ws_grek, ws_latn

ignores = [u'(...)',u' ']

def validate_name(lang, name_utf8):
    wsystem = lang.lower()
    name = unicode(name_utf8, 'utf-8')
    for ignore in ignores:
        name = name.replace(ignore, u'')
    if wsystem == 'en':
        invalids = []
    if wsystem == 'grc' or wsystem == 'la-grek':
        invalids = ws_grek.validate(name, 'all')
    elif wsystem == 'la' or wsystem == 'grc-latn':
        invalids = ws_latn.validate(name, 'all')
    else:
        return 'Unsupported writing system (%s) in PleiadesEntity/Extensions/ws_validation.py' % lang
    imsg = ''
    invalidcount = len(invalids)
    if invalidcount > 0:
        imsg = '%s invalid character(s) in name %s: ' % (invalidcount, name_utf8)
        for invalid in invalids:
            imsg += "(position %s = codepoint %X) " % (invalid['position']+1, ord(invalid['character']))
    return imsg
    
