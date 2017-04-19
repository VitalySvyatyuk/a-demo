# -*- coding: utf-8 -*-


def parse_name(name, default=None):
    """
    Function parses a given name string and returns a pair of first
    and last names. If a given string cannot be parsed (None, None)
    is returned.
    """
    bits = name.strip().split(" ")

    if name and len(bits) == 1:
        return name, default      # Sergei
    elif len(bits) == 2:
        return tuple(bits)        # Sergei Lebedev
    elif len(bits) == 3:
        return bits[1], bits[0]   # Lebedev Sergei Anatolievich

    # Unsupported name format, failing silently.
    return default, default
