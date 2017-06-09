# -*- coding: utf-8 -*-
"""
Utilitarian methods.
"""
import re

from shared.compat import methodcaller


def to_underscore(string):
    """Converts a given string from CamelCase to under_score."""
    tmp = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", tmp).lower()


def to_camelcase(string):
    """Converts a given string from under_score to CamelCase."""
    return "".join(map(methodcaller("title"), string.split("_")))


def get_engine_name(uid=None, get_demo=False):
    """Get engine name by account id"""
    # The ugliest hack for getting information about demo users
    if get_demo:
        return 'demo'
    # End of the ugliest hack
    if not uid:
        return 'default'

    if int(uid) > 1000000:
        return 'demo'
    else:
        return "default"
