# coding=utf-8
"""
Populate complex mailing lists with subscribers

This process should take place daily
"""
from datetime import datetime, date, timedelta

from django.contrib.auth.models import User
from django.db.models import Q

from massmail.models import MailingList, Subscribed
from mt4 import types as acc_types
from mt4.models import Mt4Account
from mt4_external.models_trade import Mt4Trade
from mt4_external.models_users import Mt4User
from payments.models import DepositRequest


class MarketingCampaignMetaclass(type):
    def __new__(mcs, name, bases, dict):
        not_abstract = 'is_abstract' not in dict
        cls = type.__new__(mcs, name, bases, dict)
        if not_abstract:
            cls.is_abstract = False
        return cls


class BaseMarketingCampaign(object):
    __metaclass__ = MarketingCampaignMetaclass

    MAILING_LIST_IDS = ['main']  # short identifiers of used mailing lists; do not need to be unique between campaigns

    description = ""  # Describe the purpose of the campaign here
    active = True

    def __init__(self):
        self.mailing_lists = {}
        for mailing_list in self.MAILING_LIST_IDS:
            name = u"{}_{}".format(self.__class__.__name__, mailing_list)
            # Attention: it is an ID of MailingList, not MailingList itself
            self.mailing_lists[mailing_list] = \
                MailingList.objects.get_or_create(auto_campaign_name=name,
                                                  defaults={'name': name + u" (auto)"})[0].pk

    def flush(self):
        Subscribed.objects.filter(mailing_list_id__in=self.mailing_lists.values()).delete()

    def save_subscribers(self, subscribers):
        """
        Accepts dict:from django.db.models import Q
        {mailing_list_name: [list of auth.User]}

        Or just list of auth.User, in this case, "main" mailing list is assumed
        """
        batch = []
        if not isinstance(subscribers, dict):
            subscribers = {"main": subscribers}
        for mailing_list_name, users in subscribers.items():
            for user in users:
                batch.append(Subscribed(mailing_list_id=self.mailing_lists[mailing_list_name],
                                        email=user.email, first_name=user.first_name,
                                        last_name=user.last_name))
        Subscribed.objects.bulk_create(batch)

    def update_subscriber_count(self):
        for m in MailingList.objects.filter(id__in=self.mailing_lists.values()):
            m.subscribers_count = len(m.get_emails())
            m.save()

    def get_subscribers(self):
        """
        Should return dict usable for save_subscribers
        """
        raise NotImplementedError()

    @classmethod
    def collect_all(cls):
        """
        Populates all mailing lists
        """
        for campaign in cls.__subclasses__():
            if getattr(campaign, 'is_abstract', False):
                campaign.collect_all()
            else:
                campaign().collect()

    def collect(self):
        self.flush()
        self.save_subscribers(self.get_subscribers())
        self.update_subscriber_count()