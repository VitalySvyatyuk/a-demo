# -*- coding: utf-8 -*-
__all__ = (
    "DatabaseAPI", "DatabaseCommand",
    "OPERATION_TYPES", "WITHDRAW_DEPOSIT",
    "BUY", "SELL", "BUY_LIMIT", "SELL_LIMIT",
    "BUY_STOP", "SELL_STOP",
    "WITHDRAW_DEPOSIT", "CREDIT"
)

import operator
from itertools import imap

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from shared.compat import methodcaller

from .base import BaseAPI, BaseCommand

from django.db import connections

BUY = 0
SELL = 1
BUY_LIMIT = 2
SELL_LIMIT = 3
BUY_STOP = 4
SELL_STOP = 5
WITHDRAW_DEPOSIT = 6
CREDIT = 7

OPERATION_TYPES = {
    BUY: _('buy'),
    SELL: _('sell'),
    BUY_LIMIT: _('buy limit'),
    SELL_LIMIT: _('sell limit'),
    BUY_STOP: _('buy stop'),
    SELL_STOP: _('sell stop'),
    WITHDRAW_DEPOSIT: _('withdraw/deposit'),
    CREDIT: _('credit')
}


class DatabaseAPI(BaseAPI):
    """DatabaseAPI is a tool to hold information about which one DB we need to process
    our requests. Also, it gives ability to process complex, raw SQL queries within
    commands using Django ORM connections.
    """
    #Our database names can be overriden in some places, like "demo" or "test"
    # so add prefix for it

    def __init__(self, uid=None, db=None):
        """DatabaseAPI constructor.
        uid - User ID. Sets "account" argument in queries. See DatabaseCommand.
        db = 'real' - DjangoORM database connection name w/o prefix(prefix is mt4_). See DATABASES in settings.py
        """
        self.uid = uid

        # For some reasons, DB name depents on Mt4 UserID we want to use.
        #  Because Demo users ID'd starts from 1000001
        from platforms.mt4 import get_engine_name
        self.db_name = db or get_engine_name(self.uid)

        # Get_engine_name is for SocketAPI, mostly, so we need to adapt to it.
        #  "default" Mt4 database is a "real" in django
        if self.db_name == "default":
            self.db_name = "real"

        if self.db_name not in settings.DATABASES:
            raise RuntimeError("I don't know this kind of database: %s. See DATABASES in settings.py." % self.db_name)

    def raw_query(self, qs, *args, **kwargs):
        """
        To perform any request, we can't do using Django ORM Manager.
        Result is a list of dictionaries field->value.
        """
        if not isinstance(qs, basestring):
            raise TypeError(
                "I can't use this query, i can support only raw query string. Your query type: %s" % (type(qs)))
            # for this operation, we're using backend directly
        cursor = connections[self.db_name].cursor()
        cursor.execute(qs, args or kwargs)

        #convert to list of dictionaries for portability and easier codewriting
        return dict_fetch_all(cursor)

    def query(self, qs, *args, **kwargs):
        """
        !!!Deprecated!!!
        Process raw sql query and get list of dictionaries of data, retrieved using it.
        Such as: [{'name': u'The Dude'}, ...]
        Don't use it for new code, please.
        Instead, use DjangoORM and return QuerySet from "run" command of Database Command.
        """

        # Process raw query string for backward compatability
        if not isinstance(qs, basestring):
            raise Exception(
                "I can't use this query, i can support only raw query string. Your query type: %s" % (type(qs)))
            # for this operation, we're using backend directly
        cursor = connections[self.db_name].cursor()

        # old code to support... old code
        try:
            cursor.execute(qs, args or kwargs)
        except Exception as e:
            #client.captureException()
            return [{1: 1}]  # TODO: Exceptions!!!
        return [
            dict(zip(imap(methodcaller("lower"), imap(operator.itemgetter(0), cursor.description)), row))
            for row in cursor.fetchall()
        ]


class DatabaseCommand(BaseCommand):
    """Makes writing commands for DatabaseAPI easier or... harder.

    All subclasses __should__ define at least `run` function, which
    is made to generate result. You can use Django ORM Models or DatabaseAPI.raw_query.
    """
    # Used only for old raw sql query
    # TODO: remove
    sql = None  # type: ignore

    @classmethod
    def register(cls, name=None):
        """A shortcut for registering a command.

        See BaseAPI.register_command() for details."""
        return DatabaseAPI.register_command(name, cls)

    def before(self, api, *args, **kwargs):
        kwargs.update(account=api.uid)
        return args, kwargs

    # Used only for old raw sql query
    #TODO: remove
    def run(self, api, *args, **kwargs):
        return api.query(self.sql, **kwargs)


def dict_fetch_all(cursor):
    """Returns all rows from a cursor as a dict"""
    desc = cursor.description
    return [
        dict(zip([col[0].lower() for col in desc], row))
        for row in cursor.fetchall()
    ]
