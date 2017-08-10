import fudge
from django.http import HttpResponse
from django.test import TestCase, RequestFactory

from massmail.models import MessageTemplate, Campaign, OpenedCampaign
from massmail.views import view_campaign


class TestViewCampaign(TestCase):

    @fudge.patch('massmail.models.Campaign.render_text')
    @fudge.patch('massmail.views._get_massmail_params')
    def test_view_campaign_is_text(self, rt, gmp):
        rt.is_callable().returns('Hello')
        gmp.is_callable().returns([1, 'test@email.ru'])
        self.request.GET = {'text': 'test'}
        ch = view_campaign(self.request, self.last_pk)
        self.assertTrue(isinstance(ch, HttpResponse) and ch.status_code == 200)

    @fudge.patch('massmail.models.Campaign.render_html')
    def test_view_campaign_is_html(self, rt):
        rt.is_callable().returns('Hello')
        self.request.GET = {'text': False}
        ch = view_campaign(self.request, self.last_pk)
        self.assertTrue(isinstance(ch, HttpResponse) and ch.status_code == 200)

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
