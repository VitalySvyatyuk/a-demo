# -*- coding: utf-8 -*-

"""A module with data wrappers for API return values."""

import operator
from itertools import imap

from structures import (
    Structure, Integer, Float, String, DateTime
)


class UserInfo(Structure):
    """
    Wrapper for data, returned by USERINFO, or taken from mt4_users
    databse, in case of MySQL API backend.
    """
    login = String()
    name = String()
    balance = Float()
    equity = Float()
    margin = Float()
    free = Float()
    commission = Float()
    swap = Float()
    profit = Float()
    group = String()
    credit = Float()

    # DatabaseAPI specific.
    city = String()
    state = String()
    address = String()
    country = String()
    phone = String()
    lastdate = DateTime()
    password_phone = String()
    agent_account = String()
    margin_level = Float()
    margin_free = Float()

    # SocketAPI specific
    deposit = Float()
    withdraw = Float()
    credit_deposit = Float()
    credit_withdraw = Float()

    @property
    def inout(self):
        return self.deposit - self.withdraw

    # Internal rate of return
    irr = Float()
    agent_commission = Float()


class UserHistory(Structure):
    """
    Wrapper for data, returned by USERHISTIRY, or taken from mt4_trades
    databse, in case of MySQL API backend.
    """
    login = String()
    name = String() # XXX SocketAPI specific.
    timestamp = DateTime(format="%Y.%m.%d %H:%M")
    deposit = Float()
    withdrawl = Float()
    credit = Float()
    commission = Float()
    swap = Float()
    profit = Float()

    operations = []  # type: ignore # XXX not a declarative field.

    def stats(self):
        # FIXME: make a proxy object instead?
        def attrsum(attr):
            return sum(imap(operator.attrgetter(attr), self.operations))

        return dict(("total_%s" % field, attrsum(field))
                    for field in ("swap", "profit", "commission", "volume"))


class Operation(Structure):
    """Wrapper for operation data in UserHistory object."""
    ticket = Integer()
    open_time = DateTime(format="%Y.%m.%d %H:%M")
    type = String()
    type_raw = Integer()
    volume = Float()
    symbol = String()
    open_price = Float()
    sl = Float()
    tp = Float()
    close_time = DateTime(format="%Y.%m.%d %H:%M")
    close_price = Float()
    swap = Float()
    profit = Float()
    comment = String()

    commission = Float() # XXX DatabaseAPI specific.
