# coding: utf-8
from __future__ import with_statement
import os.path
import re
import codecs

def is_middle_name(word):
    """True if the word is a a russian middle name"""
    word = word.lower()
    return word.endswith(u'вич') or word.endswith(u'вна')

# The dict with the values of russian names
# is cached in this variable on first access
RUSSIAN_NAMES = None

def is_first_name(word):
    """True if the word is a known russian first name"""
    global RUSSIAN_NAMES
    if not RUSSIAN_NAMES:
        with codecs.open(os.path.dirname(__file__) + '/russian_names.txt', encoding='utf-8') as f:
            RUSSIAN_NAMES = dict(
                (name.strip().lower(), 1) for name in
                                f.readlines()
            )
    return word.lower() in RUSSIAN_NAMES


def parse_name(name, default=None):
    """Guess, which form a given russian name is in, and return
    first, middle and last names.

    If unable to determine ony of them, return default.
    """
    bits = re.findall(u'[а-яА-ЯA-Za-z]+', name)
    bits = map(lambda name: name.title(), bits)
    if len(bits) == 1:
        return bits[0], default, default
    elif len(bits) == 2:
        # Сергеевна Дарья ?!
        if is_middle_name(bits[0]):
            return bits[1], bits[0], default
        # Дарья Сергеевна
        elif is_middle_name(bits[1]):
            return bits[0], bits[1], default
        else:
            if is_first_name(bits[0]):
                # Дарья Поплавская
                return bits[0], default, bits[1]
            else:
                # Поплавская Дарья
                return bits[1], default, bits[0]
    elif len(bits) == 3:
        if is_middle_name(bits[0]):
            if is_first_name(bits[1]):
                return bits[1], bits[0], bits[2]
            elif is_first_name(bits[2]):
                return bits[2], bits[0], bits[1]
            else:
                return bits[1], bits[0], bits[2]
        elif is_middle_name(bits[1]):
            # Дарья Сергеевна Петрова
            if is_first_name(bits[0]):
                return bits[0], bits[1], bits[2]
            # Дарья Сергеевна Петрова
            elif is_first_name(bits[2]):
                return bits[2], bits[1], bits[0]
            # Assume Дарья Сергеевна Петрова
            else:
                return bits
        elif is_middle_name(bits[2]):
            # Петрова Дарья Сергеевна
            if is_first_name(bits[0]):
                return bits[0], bits[2], bits[1]
            elif is_first_name(bits[1]):
                return bits[1], bits[2], bits[0]
            else:
                return bits[1], bits[2], bits[0]
    # Fail silently
    return default, default, default