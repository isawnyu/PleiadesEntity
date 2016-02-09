
latn_capital = {
    u"A" : "A",    # Latin capital letter a
    u"B" : "B",    # Latin capital letter b
    u"C" : "C",    # Latin capital letter c
    u"D" : "D",    # Latin capital letter d
    u"E" : "E",    # Latin capital letter e
    u"F" : "F",    # Latin capital letter f
    u"G" : "G",    # Latin capital letter g
    u"H" : "H",    # Latin capital letter h
    u"I" : "I",    # Latin capital letter i
    u"K" : "K",    # Latin capital letter k
    u"L" : "L",    # Latin capital letter l
    u"M" : "M",    # Latin capital letter m
    u"N" : "N",    # Latin capital letter n
    u"O" : "O",    # Latin capital letter o
    u"P" : "P",    # Latin capital letter p
    u"Q" : "Q",    # Latin capital letter q
    u"R" : "R",    # Latin capital letter r
    u"S" : "S",    # Latin capital letter s
    u"T" : "T",    # Latin capital letter t
    u"V" : "V",    # Latin capital letter v
    u"X" : "X",    # Latin capital letter x
    u"Y" : "Y",    # Latin capital letter y
    u"Z" : "Z"     # Latin capital letter z
}

latn_small = {
    u"a" : "a",    # Latin small letter a
    u"b" : "b",    # Latin small letter b
    u"c" : "c",    # Latin small letter c
    u"d" : "d",    # Latin small letter d
    u"e" : "e",    # Latin small letter e
    u"f" : "f",    # Latin small letter f
    u"g" : "g",    # Latin small letter g
    u"h" : "h",    # Latin small letter h
    u"i" : "i",    # Latin small letter i
    u"k" : "k",    # Latin small letter k
    u"l" : "l",    # Latin small letter l
    u"m" : "m",    # Latin small letter m
    u"n" : "n",    # Latin small letter n
    u"o" : "o",    # Latin small letter o
    u"p" : "p",    # Latin small letter p
    u"q" : "q",    # Latin small letter q
    u"r" : "r",    # Latin small letter r
    u"s" : "s",    # Latin small letter s
    u"t" : "t",    # Latin small letter t
    u"u" : "u",    # Latin capital letter u
    u"x" : "x",    # Latin capital letter x
    u"y" : "y",    # Latin capital letter y
    u"z" : "z"     # Latin capital letter z
}

legal_punctuation = {
    u"(" : "(",
    u")" : ")",
    u"." : "."
}


def validate(value, allow):
    invalids = []
    for i, c in enumerate(value):
        # verify character is within the possible general ranges, if not, mark it as invalid and move on
        # otherwise, check to make sure the character is truly valid (ranges are sparsely populated)
        cval = ord(c)
        if cval in range(65, 90) or cval in range(97, 122):
            b = None
            if 'small' in allow or 'mixed' in allow or 'all' in allow:
                try:
                    b = latn_small[c]
                except:
                    pass
            if not(b) and ('capital' in allow or 'mixed' in allow or 'all' in allow):
                try:
                    b = latn_capital[c]
                except:
                    pass
            if not(b):
                invalids.append({'position':i, 'character':c, 'reason':'illegal character in appropriate Unicode range'})
        else:
            invalids.append({'position':i, 'character':c, 'reason':'illegal character from outside appropriate Unicode range'})
    return invalids



def transliterate(value):
    transliteration = ''
    for c in value:
        b = '?'
        try:
            b = latn_small[c]
        except:
            try:
                b = latn_capital[c]
            except:
                try:
                    b = legal_punctuation[c]
                except:
                    pass
        transliteration += b
    return transliteration
    
   
        
