from unittest import skip

import fudge
from django.http import Http404, HttpResponse
from django.test import TestCase, RequestFactory
# from django.template.exceptions import TemplateDoesNotExist
from massmail.models import Unsubscribed, Campaign, MessageTemplate, MailingList
from massmail.views import unsubscribe


class TestUnsubscribe(TestCase):

    def test_uns_bad_signature_404(self):
        with self.assertRaises(Http404):
            unsubscribe(self.request, 'test@email.ru', 1)

    @fudge.patch('massmail.utils.get_signature')
    @fudge.patch('django.contrib.messages.api.success')
    def test_uns_good_signature_already_unsubscribed_no_exception(self, gs, mess):
        gs.is_callable().returns('signature')
        mess.is_callable().returns(True)

        # 4 lines below - hack for MessageMiddleware with request made by RequestFactory
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

        ch = unsubscribe(self.request, 'test@email.ru', 'signature', campaign_id=2)
        self.assertTrue(ch.status_code == 302 and ch.url == '/my/massmail/unsubscribed/test%2540email.ru/2/')

    @fudge.patch('massmail.utils.get_signature')
    def test_uns_good_signature_already_unsubscribed_throws_exception(self, gs):
        gs.is_callable().returns('signature')

        # 4 lines below - hack for MessageMiddleware with request made by RequestFactory
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

        ch = unsubscribe(self.request, 'test@email.ru', 'signature', campaign_id='BAD DATA')
        self.assertTrue(ch.status_code == 302 and ch.url == '/my/massmail/unsubscribed/test%2540email.ru/')

    @fudge.patch('massmail.utils.get_signature')
    def test_uns_good_signature_didnt_unsubs_exist_correct(self, gs):
        gs.is_callable().returns('signature')

        # 4 lines below - hack for MessageMiddleware with request made by RequestFactory
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

        ch = unsubscribe(self.request, 'test2@email.ru', 'signature')
        self.assertTrue(ch.url == '/my/massmail/unsubscribed/test2%2540email.ru/{}/' .format(self.last_pk) and
                        ch.status_code == 302)

    @fudge.patch('massmail.utils.get_signature')
    def test_uns_good_signature_didnt_unsubs_incorrect(self, gs):
        gs.is_callable().returns('signature')
        request = RequestFactory().post('test/', {'campaign_id': 'BAD'})

        # 4 lines below - hack for MessageMiddleware with request made by RequestFactory
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(request, '_messages', messages)

        ch = unsubscribe(request, 'test2@email.ru', 'signature')
        self.assertTrue(ch.url == '/my/massmail/unsubscribed/test2%2540email.ru/' and ch.status_code == 302)

    @fudge.patch('massmail.utils.get_signature')
    def test_uns_request_get_didnt_unsubscribe(self, gs):
        gs.is_callable().returns('signature')
        request = RequestFactory().get('test/', {'campaign_id': 'BAD'})

        # 4 lines below - hack for MessageMiddleware with request made by RequestFactory
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(request, '_messages', messages)

        ch = unsubscribe(request, 'test2@email.ru', 'signature', campaign_id=1)
        self.assertTrue(isinstance(ch, HttpResponse) and
                        "If you don't want to get our latest and useful information, click the button" in ch.content)

    @classmethod
    def setUpTestData(cls):
        Unsubscribed.objects.create(email='test@email.ru')
        mt = MessageTemplate.objects.create()
        mt.save()
        cls.campaign = Campaign()
        cls.campaign.languages = ['en']
        cls.campaign.template = mt
        cls.campaign.save()
        cls.last_pk = Campaign.objects.all().last().pk
        cls.request = RequestFactory().post('test/', {'campaign_id': cls.last_pk})
