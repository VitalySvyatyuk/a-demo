# -*- coding: utf-8 -*-

"""
API bindings for MetaTrader platform.

TODO:
  - Add SocketCommand.login_required attribute and call SocketAPI.login()
    automatically.
  - Add support for context managers:

    with SocketAPI() as api:
       ....
"""
from .utils import get_engine_name

__all__ = (
    "SocketAPI", "SocketCommand",
    "encode_query"
)

import random
import socket
import string
from base64 import b64encode
from itertools import cycle, izip
import logging
import time
import re

from django.conf import settings
from django.utils.datastructures import SortedDict

from .base import BaseAPI, BaseCommand
from .exceptions import MT4Error, InvalidAccount


class SocketAPI(BaseAPI):
    def __init__(self, encoding=None, engine=None, engine_subtype=None):
        self.uid = None
        self.password = None
        self.encoding = encoding or settings.MT4_SERVER_ENCODING
        self.engine_subtype = "sock" if engine_subtype is None else engine_subtype
        self._engine = engine
        super(SocketAPI, self).__init__()

    def login(self, uid, password, skip_check=False):
        """
        Emulates login behaviour, which is not implemented on MetaTrader
        server, by fetching USERINFO for a given id, password pair and
        updating API instance's attributes on success.

        Note: make sure 'info' command is registed before calling this
        method (see mt4/api/commands.py:80).
        """
        uid, password = int(uid), unicode(password)

        if not skip_check and not (uid and password):
            raise ValueError
        elif "|" in password:
            raise ValueError("Login or password contain special symbols")

        self.uid, self.password = uid, password
        if not skip_check:
            # This will raise an error if credentials are invalid
            self.old_info()

    @property
    def engine(self):
        return self._engine or get_engine_name(self.uid)

    def connect(self):
        ip, port = settings.ENGINES[self.engine][self.engine_subtype]

        # noinspection PyAttributeOutsideInit
        self.log = logging.getLogger('SocketAPI.%s:%s' % (ip, port))

        retries_left = settings.MT4_SERVER_SOCKET_RETRIES_NUMBER

        while retries_left:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(settings.MT4_SERVER_SOCKET_TIMEOUT)

            try:
                server.connect((ip, port))
                return server
            except socket.error as exc:
                self.log.exception("Error connecting to MetaTrader server:")
                if retries_left:
                    retries_left -= 1
                    self.log.exception("Trying again... (retries left: %d)" % (retries_left, ))
                    time.sleep(settings.MT4_SERVER_SOCKET_RETRY_TIMEOUT)

                else:
                    raise MT4Error(exc)

    def encoded_query(self, qs, key, sensitive_fields_regexp=None):
        """
        Splits a given query string into (command, arguments) pair,
        encodes arguments part using `encode_query()` and passess
        a newly constructed query string to `SocketAPI.query()`.
        """
        command, qs = qs.split("-", 1)
        qs_for_log = qs
        if sensitive_fields_regexp is not None:
            qs_for_log = re.sub(sensitive_fields_regexp, '******', qs_for_log)
        self.log.debug("Encoding %r with key %r", qs_for_log, key)

        # Stripping suffix and adding two random [a-z] letters,
        # not sure why, but that's what PHP code's doing ...
        command = command + random.choice(string.letters) + \
            random.choice(string.letters)

        return self.query(command + encode_query(qs, key), sensitive_fields_regexp=".*")  # Hide entire encoded query

    def _do_query(self, qs, sensitive_fields_regexp):
        if not isinstance(qs, unicode):
            qs = qs.decode("utf-8")

        retries_left = settings.MT4_SERVER_SOCKET_RETRIES_NUMBER

        while retries_left:
            server = self.connect()
            qs_for_log = qs
            if sensitive_fields_regexp is not None:
                qs_for_log = re.sub(sensitive_fields_regexp, '******', qs_for_log)
            self.log.debug("Executing query: %r", qs_for_log)
            server.send("W%s\nQUIT\n" % qs.encode(self.encoding, errors='xmlcharrefreplace'))

            try:
                data = []
                while True:
                    buf = server.recv(1024)
                    data.append(buf)
                    if len(buf) < 1024 or buf.endswith("end\r\n"):
                        break
                return data
            except socket.error as exc:
                self.log.exception("Error receiving data:")
                if retries_left:
                    retries_left -= 1
                    self.log.exception("Trying again... (retries left: %d)" % (retries_left, ))
                    time.sleep(settings.MT4_SERVER_SOCKET_RETRY_TIMEOUT)
                else:
                    raise MT4Error(exc)

            finally:
                server.close()

    def query(self, qs, decode=True, sensitive_fields_regexp=None):
        """
        Sends a given query string to the server, then:
        a) parses response into (status, payload) and returns payload
           part if status is 'OK' else raises APIError
        b) returns raw response if it doesn't match <status><payload>
           scheme
        """
        retries_left = settings.MT4_SERVER_SOCKET_RETRIES_NUMBER

        while retries_left:
            data = self._do_query(qs, sensitive_fields_regexp)
            try:
                data = "".join(data)
            except TypeError:
                data = None
                self.log.debug("Got nothing")
            else:
                if decode:
                    data = data.decode(self.encoding)
                data = data.strip()
                self.log.debug("Got: %r", data)

            # Possible error cases:
            # a) nothing received
            if not data:
                if retries_left:
                    self.log.exception("Received nothing from Mt4 server.")
                    self.log.exception("Trying again... (retries left: %d)" % (retries_left, ))
                    retries_left -= 1
                    if retries_left <= 0:
                        raise MT4Error("Received nothing from Mt4 server.")
                    time.sleep(settings.MT4_SERVER_SOCKET_RETRY_TIMEOUT)
            else:
                break

        # b) response in unexpected format, i.e. not <status>...end\r\n
        try:
            status, payload = data.split("\r\n", 1)
            if payload.endswith('\r\nend'):
                payload = payload[:-len("\r\nend")]

            assert status in ("OK", "ERROR")
        except (ValueError, AssertionError):
            # Note: if response is in unexpected format i.e. not
            # <status>...end\r\n we return it as a raw string, allowing
            # the calling function to handle it.
            return data

        # c) error status received
        if status == "ERROR":
            raise MT4Error(payload)
        else:
            return payload


class SocketCommand(BaseCommand):
    """Makes writing commands for SocketAPI easier.

    All subclasses __should__ define at least `command` attribute,
    which is a string passed to MetaTrader API before arguments (see
    SocketCommand.before() for implementation details).
    """
    command, encoded, binary = None, False, False  # type: ignore

    @classmethod
    def register(cls, name=None):
        """A shortcut for registering a command.

        See BaseAPI.register_command() for details."""
        SocketAPI.register_command(name, cls)

    def before(self, api, kwargs=None, **extra):
        """Formats given keyword arguments in MetaTrader format.

        <command>-arg1=val1|arg2=val2|...
        """
        # Thanks to the bug in NEWACCOUNT, we are forced to use
        # SortedDict.

        def ensure_unicode(string):
            if isinstance(string, str):
                return string.decode('cp1251')
            return unicode(string)

        kwargs = SortedDict(kwargs or {})
        kwargs.update(extra)

        key = kwargs.pop("key", None)
        if self.encoded and not key:
            raise MT4Error("Key required to call %r" % self)

        qs = u"%s-%s" % (self.command.upper(),
                         u"|".join(u"{}={}".format(*map(ensure_unicode, pair)) for pair in kwargs.iteritems()))

        return (qs, ), {"key": key, "sensitive_fields_regexp": getattr(self, "sensitive_fields_regexp", None)}

    def run(self, api, qs, key=None, sensitive_fields_regexp=None):
        """Executes a command.

        If `encoded` attribute it truthy, SocketAPI.encoded_query() is
        used instead of simple SocketAPI.query().
        """
        if self.encoded:
            result = api.encoded_query(qs, key, sensitive_fields_regexp)
        else:
            result = api.query(qs, (not self.binary), sensitive_fields_regexp=sensitive_fields_regexp)

        # HACK: USERINFO returns an error with the ERROR: prefix,
        # so we need to do the manual check here.
        if result.startswith("Invalid Account"):
            raise InvalidAccount(api.uid)
        else:
            return result


# Santa's little helpers.


def xor_crypt(data, key):
    if isinstance(data, unicode):
        data = data.encode(settings.MT4_SERVER_ENCODING)
    return "".join(chr(ord(x) ^ ord(y))
                   for (x, y) in izip(data, cycle(key)))


def encode_query(data, key):
    """
    Returns encoded (XOR + base64) version of the data string, using
    a given key.
    """
    return b64encode(xor_crypt(data, key))


