# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from geobase.models import Country
from massmail.models import MailingList, Unsubscribed
from profiles.models import UserProfile


class TestMailingList(TestCase):

    def test_str(self):
        ml = MailingList()
        ml.name = 'test'
        ml.subscribers_count = 2
        self.assertEqual(str(ml), '%s (%s emails)' % (ml.name, ml.subscribers_count))

    def test_countries(self):
        ml = MailingList()
        self.assertEqual(ml.countries.get(pk=1), Country.objects.get(pk=1))
        ml.languages = ['ru']
        self.assertEqual(ml.countries.get(pk=1), Country.objects.get(pk=1))

    def test_eval_query_no_query(self):
        self.ml.query = None
        self.assertEqual(self.ml._eval_query(), {})

    def test_eval_query_with_query_user_qs(self):
        self.ml.query = 'User.objects.all()'
        self.assertEqual(self.ml._eval_query(), {u'teste1r@uptrader.us': (u'Иван', u'Дорн'),
                                                 u'tester2@uptrader.us': (u'Mr', u'Tester 2'),
                                                 u'tester@uptrader.us': (u'Mr', u'Tester')
                                                 }
                         )

    def test_eval_query_with_query_no_qs(self):
        self.ml.query = '[User.objects.get(pk=3)]'
        self.assertEqual(self.ml._eval_query(), {'tester@uptrader.us': ('Mr', 'Tester')})

    def test_get_emails_no_lang_no_ignore_unsub(self):
        self.ml.save()
        unsubs = Unsubscribed()
        unsubs.email = 'tester@uptrader.us'
        unsubs.mailing_list = self.ml
        unsubs.save()

        self.assertEqual(self.ml.get_emails(), {u'tester2@uptrader.us': (u'Mr', u'Tester 2'),
                                                u'teste1r@uptrader.us': (u'Иван', u'Дорн')
                                                }
                         )

    def test_get_phone_numbers(self):
        self.ml.save()
        ch1 = UserProfile.objects.all().first()
        ch1.phone_mobile = '89523812603'
        validation, created = ch1.user.validations.get_or_create(key="phone_mobile")
        validation.is_valid = True
        validation.save()
        ch1.save()
        ch1 = UserProfile.objects.all().last()
        ch1.phone_mobile = '89312216754'
        ch1.save()
        validation, created = ch1.user.validations.get_or_create(key="phone_mobile")
        validation.is_valid = True
        validation.save()
        ch = self.ml.get_phone_numbers()
        self.assertEqual(ch, {u'89523812603', '89312216754'})

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', 'django-shared/geobase/tests/fixtures/test_geobase.json', verbosity=0)
        call_command('loaddata', 'django-gc-shared/profiles/tests/fixtures/test_users.json', verbosity=0)
        cls.ml = MailingList()
