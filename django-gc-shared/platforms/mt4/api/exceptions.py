# -*- coding: utf-8 -*-

import re

from platforms.exceptions import PlatformError


class MT4Error(PlatformError):
    """Generic Mt4 API exception class."""
    @property
    def code(self):
        """
        Returns an integer error code for the exception.
        Returns -1 if the exception doesn't have any error codes in it.
        """
        if len(self.args) == 2:  # APIError raised by Custom API
            return int(self.args[0])
        try:
            match = re.search("invalid data \[(?P<code>\d+)\]", unicode(self))
            return int(match.group("code"))
        except (ValueError, AttributeError):
            return -1


class InvalidAccount(MT4Error):
    """
    Exception, raised, when the query with auth data (LOGIN=|PASSWORD=)
    return `Invalid Account` response or when there's no user info for
    an account with a given `account_id`, in case of the DatabaseAPI.
    """
