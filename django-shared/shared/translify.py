# -*- coding: utf-8 -*-

symbol_map = [
    (u"А", "A"),
    (u"Б", "B"),
    (u"В", "V"),
    (u"Г", "G"),
    (u"Д", "D"),
    (u"Е", "E"),
    (u"Ё", "E"),
    (u"Ж", "ZH"),
    (u"З", "Z"),
    (u"И", "I"),
    (u"Й", "I"),
    (u"К", "K"),
    (u"Л", "L"),
    (u"М", "M"),
    (u"Н", "N"),
    (u"О", "O"),
    (u"П", "P"),
    (u"Р", "R"),
    (u"С", "S"),
    (u"Т", "T"),
    (u"У", "U"),
    (u"Ф", "F"),
    (u"Х", "KH"),
    (u"Ц", "TC"),
    (u"Ч", "CH"),
    (u"Ш", "SH"),
    (u"Щ", "SHCH"),
    (u"Ъ", ""),
    (u"Ы", "Y"),
    (u"Ь", ""),
    (u"Э", "E"),
    (u"Ю", "IU"),
    (u"Я", "IA")
]

def translify(in_string):
    """
    Транслит русского текста по ГОСТ 52535.1-2006 (применяется для транслитерации
    русских имен для загранпаспортов с 2010 года)
    """
    translit = in_string
    for symb_in, symb_out in symbol_map:
        translit = translit.replace(symb_in, symb_out)
        translit = translit.replace(symb_in.lower(), symb_out.lower())

    return translit