# -*- coding: utf-8 -*-
import logging
import random
import re
import string
from base64 import b64encode
from itertools import cycle, izip


re_ip = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

log = logging.getLogger(__name__)


def xor_crypt(data, key):
    return "".join(chr(ord(x) ^ ord(y))
                   for (x, y) in izip(data, cycle(key)))


def encode_query(data, key):
    """
    Returns encoded (XOR + base64) version of the data string, using
    a given key.
    """
    return b64encode(xor_crypt(data, key))


def get_ip(request):
    """
    Function tries to extract remote IP address from request headers
    (REMOTE_ADDR, HTTP_X_FORWARDED_FOR). Returnes IP address or an
    empty string, if no IP address can be extracted.
    """
    raw_ip = request.META.get("HTTP_X_FORWARDED_FOR",
                          request.META.get("REMOTE_ADDR"))
    if raw_ip:
        # Some proxy servers use a list of IP addreses as a value for
        # the above headers, in such a case only the first IP address
        # is used (c) django-tracking
        match = re_ip.match(raw_ip)
        if match:
            return match.group(0)
    return ""


def create_password(size=8, only_digits=False):
    """Function generates a random password string of a given length."""
    while True:
        charset = string.digits
        if not only_digits:
            charset += string.letters
        password = ''.join(random.choice(charset) for _ in xrange(size))
        if only_digits:
            return password
        # TODO: Validate that there's at least two symbols of each type.
        if re.search('[0-9]', password) and re.search('[a-z]', password) and \
            re.search('[A-Z]', password):
            return password
