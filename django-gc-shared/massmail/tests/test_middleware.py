import fudge
from django.test import TestCase, RequestFactory

from massmail.middleware import MassMailMiddleware
from massmail.models import MessageTemplate, Campaign, OpenedCampaign


class TestMassMailMiddleware(TestCase):
    def test_process_response_not_text(self):
        response = {'content-type': 'gi'}
        self.assertEqual(self.middle.process_response(self.request, response), response)

    @fudge.patch('massmail.views._get_massmail_params')
    def test_process_response_text_no_campaign_email(self, f):
        f.is_callable().returns((None, None))
        response = {'content-type': 'text/html'}
        self.assertEqual(self.middle.process_response(self.request, response), response)

    @fudge.patch('massmail.views._get_massmail_params')
    def test_process_response_text_with_campaign_email(self, f):
        mt = MessageTemplate()
        mt.save()
        c = Campaign.objects.create(template=mt, send_once=True, send_period=False, name='test_campaign',
                                    _lock=False, is_active=False, send_once_datetime='2017-10-9', is_sent=False)

        f.is_callable().returns((c, 'test_email'))
        OpenedCampaign.objects.create(opened=False, clicked=False, campaign=c, email='test_email')
        response = {'content-type': 'text/html'}
        self.assertEqual(self.middle.process_response(self.request, response), response)

    @classmethod
    def setUpTestData(cls):
        cls.middle = MassMailMiddleware()
        cls.request = RequestFactory().get('test/')
