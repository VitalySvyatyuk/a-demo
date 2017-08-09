# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from massmail.models import Unsubscribed, make_profile_subscription_empty


class TestUnsubscr(TestCase):

    def test_str(self):
        self.assertEqual(str(self.uns), self.uns.email)

    def test_make_profile_subs_empty(self):
        make_profile_subscription_empty(1, self.uns, True)

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', 'django-shared/geobase/tests/fixtures/test_geobase.json', verbosity=0)
        call_command('loaddata', 'django-gc-shared/profiles/tests/fixtures/test_users.json', verbosity=0)
        cls.uns = Unsubscribed()
        cls.uns.email = User.objects.get(pk=3).email
