# -*- coding: utf-8 -*-
from django.db import models

from currencies import currencies
from currencies.money import Money
from platforms.model_manager import AdvancedManager
from platforms.types import (
    get_account_type)
from shared.werkzeug_utils import cached_property


class UserManager(AdvancedManager):
    """Advanced functions for User model from Mt4 database
    """

    def in_group(self, group_name):
        return self.filter(group=group_name)


class AbstractUser(models.Model):
    # Client's login
    login = models.IntegerField(primary_key=True, db_column='LOGIN')
    # Client trade group on server
    group = models.CharField(max_length=48, db_column='GROUP')
    # Flag of account activity (1 - active, 0 - not active)
    enable = models.IntegerField(db_column='ENABLE')
    # Flag of account's permission to change password (1 - password change allowed, 0 - password change prohibited)
    enable_change_pass = models.IntegerField(db_column='ENABLE_CHANGE_PASS')
    # Flag of setting read-only mode without trading (1 - read-only mode on, 0 - read-only mode off)
    enable_readonly = models.IntegerField(db_column='ENABLE_READONLY')
    # Phone password
    password_phone = models.CharField(max_length=96, db_column='PASSWORD_PHONE')
    # Name of account owner
    name = models.CharField(max_length=384, db_column='NAME')
    # Country
    country = models.CharField(max_length=96, db_column='COUNTRY')
    # City
    city = models.CharField(max_length=96, db_column='CITY')
    # State (area, region, etc.)
    state = models.CharField(max_length=96, db_column='STATE')
    # Zip/Postal code
    zipcode = models.CharField(max_length=48, db_column='ZIPCODE')
    # Address
    address = models.CharField(max_length=384, db_column='ADDRESS')
    # Phone
    phone = models.CharField(max_length=96, db_column='PHONE')
    # Email
    email = models.CharField(max_length=144, db_column='EMAIL')
    # Comment
    comment = models.CharField(max_length=192, db_column='COMMENT')
    # SIN, TIN or other unique identifiers of account owner
    id = models.CharField(max_length=96, db_column='ID')
    # Resident/Nonresident status
    status = models.CharField(max_length=48, db_column='STATUS')
    # Registration date
    regdate = models.DateTimeField(db_column='REGDATE')
    # Time of account's last access to trade server (doesn't update in MySQL in real time)
    lastdate = models.DateTimeField(db_column='LASTDATE')
    # Leverage
    leverage = models.IntegerField(db_column='LEVERAGE')
    # Agent account number
    agent_account = models.IntegerField(db_column='AGENT_ACCOUNT')
    # Time of account record last update on trade server in UNIX format (server time)
    timestamp = models.IntegerField(db_column='TIMESTAMP')
    # Current balance (the sum of all deposits and withdrawals to/from an investment account)
    balance = models.FloatField(db_column='BALANCE')
    # Balance as of the end of previous month
    prevmonthbalance = models.FloatField(db_column='PREVMONTHBALANCE')
    # Balance at the end of previous day
    prevbalance = models.FloatField(db_column='PREVBALANCE')
    # Credit
    credit = models.FloatField(db_column='CREDIT')
    # Charged annual interest rate
    interestrate = models.FloatField(db_column='INTERESTRATE')
    # Taxes rate calculated as free margin interest rate (annual interest rate)
    taxes = models.FloatField(db_column='TAXES')
    # Flag of generating daily reports (1 - reports are allowed, 0 - reports are prohibited)
    send_reports = models.IntegerField(db_column='SEND_REPORTS')
    # Account color ?
    user_color = models.IntegerField(db_column='USER_COLOR')
    # Current equity (the total monetary value)
    equity = models.FloatField(db_column='EQUITY')
    # Size of reserved margin
    margin = models.FloatField(db_column='MARGIN')
    # Margin level
    margin_level = models.FloatField(db_column='MARGIN_LEVEL')
    # Size of free margin
    margin_free = models.FloatField(db_column='MARGIN_FREE')
    # Timestamp for modification of record in MySQL database
    modify_time = models.DateTimeField(db_column='MODIFY_TIME')

    class Meta:
        abstract = True
        db_table = u'mt4_users'
        app_label = 'external'

    def __unicode__(self):
        return u"%s (%s)" % (self.login, self.group)

    objects = UserManager()

    @cached_property
    def currency(self):
        """
        Get client currency.
        """
        return currencies.get_by_group(self.group) or currencies.USD

    @property
    def balance_money(self):
        """
        Get balance as Money object.
        """
        return Money(self.balance, self.currency)

    @property
    def equity_money(self):
        """
        Get equity as Money object.
        """
        return Money(self.balance, self.currency)

    @cached_property
    def account_type(self):
        """
        Type of account: demo/real/etc
        """
        return get_account_type(self.group)

    @cached_property
    def accounts(self):
        """
        Connected account objects.
        """
        from platforms.models import TradingAccount
        return TradingAccount.objects.filter(mt4_id=self.login)


# Classes for additional databases of the same schema: Real, Demo and Archive.
# Control of models routing is in router.py
class RealUser(AbstractUser):
    pass


class DemoUser(AbstractUser):
    pass


class ArchiveUser(AbstractUser):
    pass


mt4_user = {
    "db_archive": ArchiveUser,
    "demo": DemoUser,
    "real": RealUser,
    "default": RealUser,
}
