# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import Context
from django.test import TestCase
from massmail.models import Campaign, MailingList, Subscribed, Unsubscribed, SentMessage
import fudge
from massmail.models import MessageTemplate


class TestSend(TestCase):

    def test_send_self_lock(self):
        self.campaign.is_active = True
        self.campaign._lock = True
        self.assertEqual(self.campaign.send(), None)

    def test_send_self_inactive(self):
        self.campaign.is_active = False
        self.campaign._lock = False
        self.assertEqual(self.campaign.send(), None)

    @fudge.patch('massmail.models.Campaign.get_context')
    def test_send_no_negative_ml_rev_previous_type_all(self, gbc):
        gbc.is_callable().returns(Context({'None': True}))
        settings.MASSMAIL_DEFAULT_FROM_EMAIL = 'gokadi2@yandex.ru'
        settings.MASSMAIL_DEFAULT_REPLY_TO = 'gokadi@yandex.ru'
        sm = SentMessage()
        sm.email = 'tester2@uptrader.us'
        sm.campaign = self.campaign
        sm.save()
        self.campaign.security_notification = True
        self.campaign.is_active = True
        self.campaign._lock = False

        self.camp2.sent_messages.create()
        self.campaign.previous_campaigns = [self.camp2]
        self.campaign.previous_campaigns_type = 'all'
        self.campaign.send(mail_list={'tester2@uptrader.us': ('Mr', 'Tester 2'),
                                      'teste1r@uptrader.us': ('Иван', 'Дорн')})

    @fudge.patch('massmail.models.Campaign.get_context')
    def test_send_no_negative_ml_rev_previous_type_none_founded_user(self, gbc):
        gbc.is_callable().returns(Context({'None': True}))
        settings.MASSMAIL_DEFAULT_FROM_EMAIL = 'gokadi2@yandex.ru'
        settings.MASSMAIL_DEFAULT_REPLY_TO = 'gokadi@yandex.ru'
        sm = SentMessage()
        sm.email = 'tester2@uptrader.us'
        sm.campaign = self.campaign
        sm.save()
        self.campaign.security_notification = True
        self.campaign.is_active = True
        self.campaign._lock = False
        self.campaign.send_in_private = True

        self.camp2.sent_messages.create(email='teste1r@uptrader.us')
        self.campaign.previous_campaigns = [self.camp2]
        self.campaign.previous_campaigns_type = 'none'
        self.campaign.send(mail_list={'tester2@uptrader.us': ('Mr', 'Tester 2'),
                                      'teste1r@uptrader.us': ('Иван', 'Дорн')})

    @fudge.patch('massmail.models.Campaign.get_context')
    def test_send_no_negative_ml_rev_previous_type_none_no_founded_user(self, gbc):
        gbc.is_callable().returns(Context({'None': True}))
        settings.MASSMAIL_DEFAULT_FROM_EMAIL = 'gokadi2@yandex.ru'
        settings.MASSMAIL_DEFAULT_REPLY_TO = 'gokadi@yandex.ru'
        sm = SentMessage()
        sm.email = 'tester2@uptrader.us'
        sm.campaign = self.campaign
        sm.save()
        self.campaign.security_notification = True
        self.campaign.is_active = True
        self.campaign._lock = False
        self.campaign.send_in_private = True

        self.camp2.sent_messages.create(email='teste1r@uptrader.us')
        self.campaign.previous_campaigns = [self.camp2]
        self.campaign.previous_campaigns_type = 'none'
        self.campaign.send(mail_list={'tester2@uptrader.us': ('Mr', 'Tester 2'),
                                      'teste1r@uptradr.us': ('Иван', 'Дорн')})

    @fudge.patch('massmail.models.Campaign.get_context')
    def test_send_no_negative_ml_rev_previous_type_read(self, gbc):
        gbc.is_callable().returns(Context({'None': True}))
        settings.MASSMAIL_DEFAULT_FROM_EMAIL = 'gokadi2@yandex.ru'
        settings.MASSMAIL_DEFAULT_REPLY_TO = 'gokadi@yandex.ru'
        sm = SentMessage()
        sm.email = 'tester2@uptrader.us'
        sm.campaign = self.campaign
        sm.save()
        self.campaign.security_notification = True
        self.campaign.is_active = True
        self.campaign._lock = False

        self.campaign.previous_campaigns = [self.camp2]
        self.campaign.previous_campaigns_type = 'read'
        self.campaign.send(mail_list={'tester2@uptrader.us': ('Mr', 'Tester 2'),
                                      'teste1r@uptrader.us': ('Иван', 'Дорн')})

    @fudge.patch('massmail.models.Campaign.get_context')
    def test_send_no_negative_ml_rev_previous_type_unread(self, gbc):
        gbc.is_callable().returns(Context({'None': True}))
        settings.MASSMAIL_DEFAULT_FROM_EMAIL = 'gokadi2@yandex.ru'
        settings.MASSMAIL_DEFAULT_REPLY_TO = 'gokadi@yandex.ru'
        sm = SentMessage()
        sm.email = 'tester2@uptrader.us'
        sm.campaign = self.campaign
        sm.save()
        self.campaign.security_notification = True
        self.campaign.is_active = True
        self.campaign._lock = False

        self.camp2.clicks.create(email='teste1r@uptrader.us', opened=True)
        self.campaign.previous_campaigns = [self.camp2]
        self.campaign.previous_campaigns_type = 'unread'
        self.campaign.send(mail_list={'tester2@uptrader.us': ('Mr', 'Tester 2'),
                                      'teste1r@uptrader.us': ('Иван', 'Дорн')})

    @fudge.patch('massmail.models.Campaign.get_context')
    def test_send_no_negative_ml_rev_previous_type_clicked(self, gbc):
        gbc.is_callable().returns(Context({'None': True}))
        settings.MASSMAIL_DEFAULT_FROM_EMAIL = 'gokadi2@yandex.ru'
        settings.MASSMAIL_DEFAULT_REPLY_TO = 'gokadi@yandex.ru'
        sm = SentMessage()
        sm.email = 'tester2@uptrader.us'
        sm.campaign = self.campaign
        sm.save()
        self.campaign.security_notification = True
        self.campaign.is_active = True
        self.campaign._lock = False

        self.camp2.clicks.create(email='teste1r@uptrader.us', opened=True)
        self.campaign.previous_campaigns = [self.camp2]
        self.campaign.previous_campaigns_type = 'clicked'
        self.campaign.send(mail_list={'tester2@uptrader.us': ('Mr', 'Tester 2'),
                                      'teste1r@uptrader.us': ('Иван', 'Дорн')})

    @fudge.patch('massmail.models.Campaign.get_context')
    def test_send_no_negative_ml_rev_previous_type_unclicked_len_2(self, gbc):
        gbc.is_callable().returns(Context({'None': True}))
        settings.MASSMAIL_DEFAULT_FROM_EMAIL = 'gokadi2@yandex.ru'
        settings.MASSMAIL_DEFAULT_REPLY_TO = 'gokadi@yandex.ru'
        sm = SentMessage()
        sm.email = 'tester2@uptrader.us'
        sm.campaign = self.campaign
        sm.save()
        self.campaign.security_notification = True
        self.campaign.is_active = True
        self.campaign._lock = False

        self.camp2.clicks.create(email='teste1r@uptrader.us', clicked=True)
        self.campaign.previous_campaigns = [self.camp2]
        self.campaign.previous_campaigns_type = 'unclicked'
        # self.campaign.custom_email_from = None
        self.campaign.send(mail_list={'tester2@uptrader.us': ('Mr', 'Tester 2'),
                                      'teste1r@uptrader.us': ('Иван', 'Дорн')})

    @fudge.patch('massmail.models.Campaign.get_context')
    def test_send_no_negative_ml_rev_previous_type_unclicked_len_more_than_2(self, gbc):
        gbc.is_callable().returns(Context({'None': True}))
        settings.MASSMAIL_DEFAULT_FROM_EMAIL = 'gokadi2@yandex.ru'
        settings.MASSMAIL_DEFAULT_REPLY_TO = 'gokadi@yandex.ru'
        sm = SentMessage()
        sm.email = 'tester2@uptrader.us'
        sm.campaign = self.campaign
        sm.save()
        self.campaign.security_notification = True
        self.campaign.is_active = True
        self.campaign._lock = False

        self.camp2.clicks.create(email='teste1r@uptrader.us', opened=True)
        self.campaign.previous_campaigns = [self.camp2]
        self.campaign.previous_campaigns_type = 'unclicked'
        self.campaign.custom_email_from = 'from_email'
        self.campaign.send(mail_list={'tester2@uptrader.us': ('Mr', 'Tester 2'),
                                      'teste1r@uptrader.us': ('Иван', 'Дорн', {})}, global_template_context={})

    @fudge.patch('massmail.models.Campaign.get_context')
    def test_send_no_negative_ml_rev_previous_type_unclicked_bad_email(self, gbc):
        gbc.is_callable().returns(Context({'None': True}))
        settings.MASSMAIL_DEFAULT_FROM_EMAIL = 'gokadi2@yandex.ru'
        settings.MASSMAIL_DEFAULT_REPLY_TO = 'gokadi@yandex.ru'
        sm = SentMessage()
        sm.email = 'tester2@uptrader.us'
        sm.campaign = self.campaign
        sm.save()
        self.campaign.security_notification = True
        self.campaign.is_active = True
        self.campaign._lock = False

        self.camp2.clicks.create(email='плохая почта', opened=True)
        self.campaign.previous_campaigns = [self.camp2]
        self.campaign.previous_campaigns_type = 'unclicked'
        # self.campaign.custom_email_from = None
        self.campaign.send(mail_list={'tester2@uptrader.us': ('Mr', 'Tester 2'),
                                      'плохая почта': ('Иван', 'Дорн')})

    @fudge.patch('massmail.models.Campaign.get_context')
    def test_send_negative_ml(self, gbc):
        gbc.is_callable().returns(Context({'None': True}))
        settings.MASSMAIL_DEFAULT_FROM_EMAIL = 'gokadi2@yandex.ru'
        settings.MASSMAIL_DEFAULT_REPLY_TO = 'gokadi@yandex.ru'
        self.campaign.security_notification = False
        self.campaign.is_active = True
        self.campaign._lock = False
        self.campaign.send(mail_list={'tester2@uptrader.us': ('Mr', 'Tester 2'),
                                                'teste1r@uptrader.us': ('Иван', 'Дорн')})

    @classmethod
    def setUpTestData(cls):
        mt = MessageTemplate.objects.create()
        mt.save()
        cls.campaign = Campaign()
        cls.campaign.languages = ['en']



        nml = MailingList.objects.create()
        nml.save()
        cls.campaign.template = mt
        cls.campaign.save()  # don't remove, we need to save before manytomany assignment
        cls.camp2 = Campaign()
        cls.camp2.template = mt
        cls.camp2.save()
        ml = MailingList.objects.create()
        ml.subscribers_count = 2

        subs = Subscribed()
        subs.email = 'tester@uptrader.us1'
        subs.mailing_list = ml
        subs.save()

        subs = Subscribed()
        subs.email = 'tester@uptrader.us1'
        subs.mailing_list = nml
        subs.save()

        unsubs = Unsubscribed()
        unsubs.email = 'tester2@uptrader.us'
        unsubs.mailing_list = ml
        unsubs.save()

        ml.save()

        cls.campaign.mailing_list = [ml]
        cls.campaign.negative_mailing_list = [nml]
        cls.campaign.previous_campaigns = [cls.camp2]
        cls.campaign.save()

        sm = SentMessage()
        sm.email = 'tester@uptrader.us1'
        sm.campaign = cls.campaign
        sm.save()
