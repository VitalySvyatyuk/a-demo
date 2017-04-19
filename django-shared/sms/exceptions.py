# -*- coding: utf-8 -*-

from django.utils.encoding import force_unicode


class BackendCoreError(Exception):
    """
    Exception class raised for errors, not intended to be displayed
    to the user.
    """
    def __init__(self, *args):
        super(BackendCoreError, self).__init__(*map(force_unicode, args))


class BackendUserError(Exception):
    """
    Exception class raised for errors sent back to the user as non
    field errors in SendSMSForm.
    """
    def __init__(self, *args):
        super(BackendUserError, self).__init__(*map(force_unicode, args))
