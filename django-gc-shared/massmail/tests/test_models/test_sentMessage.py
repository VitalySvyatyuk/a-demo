from django.test import TestCase
from massmail.models import SentMessage, Campaign


class TestSentMessage(TestCase):

    def test_str(self):
        c = Campaign()
        c.name = 'test_campaign'
        sm = SentMessage()
        sm.campaign = c
        sm.email = 'test_mail'
        self.assertEqual(str(sm), 'test_campaign: test_mail')
