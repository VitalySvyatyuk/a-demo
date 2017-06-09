# -*- coding: utf-8 -*-

"""
MetaTrader 4 Server API (https://support.metaquotes.net/ru/docs/mt4/api/server_api).
Based on socket communication with custom-made MT4 plugins.
Historically the only one supported for Grand Capital.
Just one of many supported for UpTrader.
"""

__all__ = ("DatabaseAPI", "SocketAPI", "CustomAPI")

from base import *
from custom import *
from database import *
from exceptions import *
from shared.werkzeug_utils import import_string
from sock import *
from wrappers import *


def autodiscover():
    """
    Iterates over INSTALLED_APPS and collects API commands from
    <appdir>/api/commands.py modules, commands still need to be
    registered explicitly, that is:

      a) by calling <Command>.register()

      b) by calling <API>.register_command(<CommandClass>) or
                    <API>.register_command(<command_function>)
    """
    for app in settings.INSTALLED_APPS:
        try:
            import_string("%s.api.commands" % app)
        except (ImportError, AttributeError):
            pass
