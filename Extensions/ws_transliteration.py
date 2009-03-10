from pleiades.transliteration import ws_grek, ws_latn

def transliterate_name(lang, name_utf8):
    wsystem = lang.lower()
    name = unicode(name_utf8, 'utf-8')
    if wsystem == 'grc' or wsystem == 'la-grek':
        transliteration = ws_grek.transliterate(name)
    elif wsystem == 'la' or wsystem == 'grc-latn':
        transliteration = ws_latn.transliterate(name)
    else:
        return 'Unsupported writing system (%s) in PleiadesEntity/Extensions/ws_transliteration.py' % lang
    return transliteration
    