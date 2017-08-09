from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, RequestFactory

from massmail.models import Campaign, MessageTemplate
from massmail.views import resubscribe


class TestResubscribe(TestCase):

    def test_res_request_with_correct_email_no_exception(self):
        ch = resubscribe(self.request, self.request.user.email, self.last_pk)
        correct = '/my/massmail/unsubscribed/tester%2540uptrader.us/{}/'.format(self.last_pk)
        self.assertTrue(ch.status_code == 302 and ch.url == correct)

    def test_res_request_with_correct_email_with_exception(self):
        ch = resubscribe(self.request, self.request.user.email, 'bad_campaign id')
        correct = '/my/massmail/unsubscribed/tester%2540uptrader.us/'
        self.assertTrue(ch.status_code == 302 and ch.url == correct)

    def test_res_request_with_incorrect_email(self):
        ch = resubscribe(self.request, 'bad@email.bad', self.last_pk)
        self.assertTrue(ch.status_code == 302 and ch.url == '/')

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', 'django-shared/geobase/tests/fixtures/test_geobase.json', verbosity=0)
        call_command('loaddata', 'django-gc-shared/profiles/tests/fixtures/test_users.json', verbosity=0)
        cls.request = RequestFactory().get('test/')
        cls.request.user = User.objects.get(pk=3)
        mt = MessageTemplate.objects.create()
        mt.save()
        cls.campaign = Campaign()
        cls.campaign.languages = ['en']
        cls.campaign.template = mt
        cls.campaign.unsubscribed = 1
        cls.campaign.save()
        cls.last_pk = Campaign.objects.all().last().pk
