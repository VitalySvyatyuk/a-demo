import fudge
from django.test import TestCase, RequestFactory

from massmail.models import MessageTemplate, Campaign, OpenedCampaign
from massmail.views import serve_static


class TestServeStatic(TestCase):

    @fudge.patch('massmail.views._get_massmail_params')
    @fudge.patch('django.views.static.serve')
    def test_serve_static(self, gmp, serve):
        gmp.is_callable().returns([self.campaign, 'test@email.ru'])
        serve.is_callable().returns('succeed')
        ch = serve_static(self.request, path='apps/')
        self.assertEqual(ch, 'succeed')

    @classmethod
    def setUpTestData(cls):
        cls.request = RequestFactory().get('test/')
        mt = MessageTemplate.objects.create()
        mt.save()
        cls.campaign = Campaign()
        cls.campaign.languages = ['en']
        cls.campaign.template = mt
        cls.campaign.save()
        cls.last_pk = Campaign.objects.all().last().pk
        OpenedCampaign.objects.create(email='test@email.ru', campaign=cls.campaign, opened=False)
