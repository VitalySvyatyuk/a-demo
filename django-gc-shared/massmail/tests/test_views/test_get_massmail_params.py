import fudge
from django.test import TestCase, RequestFactory

from massmail.models import MessageTemplate, Campaign
from massmail.views import _get_massmail_params


class TestGetMassmailParams(TestCase):

    @fudge.patch('massmail.utils.get_signature')
    def test_get_massmail_params_good_id(self, gs):
        gs.is_callable().returns('signature')
        self.request.GET = {'campaign_id': self.last_pk,
                            'email': 'test@email.ru',
                            'signature': 'signature'
                            }
        self.assertEqual(_get_massmail_params(self.request), (self.campaign, 'test@email.ru'))

    @fudge.patch('massmail.utils.get_signature')
    def test_get_massmail_params_bad_id_id(self, gs):
        gs.is_callable().returns('signature')
        self.request.GET = {'campaign_id': 1,
                            'email': 'test@email.ru',
                            'signature': 'signature'
                            }
        self.assertEqual(_get_massmail_params(self.request), (None, 'test@email.ru'))

    @classmethod
    def setUpTestData(cls):
        mt = MessageTemplate.objects.create()
        mt.save()
        cls.campaign = Campaign()
        cls.campaign.languages = ['en']
        cls.campaign.template = mt
        cls.campaign.save()
        cls.last_pk = Campaign.objects.all().last().pk
        cls.request = RequestFactory().get('test/')
