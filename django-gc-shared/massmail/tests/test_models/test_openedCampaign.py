from django.test import TestCase
from massmail.models import OpenedCampaign, Campaign


class TestOpenedCampaign(TestCase):

    def test_str(self):
        c = Campaign()
        c.name = 'test_campaign'
        oc = OpenedCampaign()
        oc.campaign = c
        oc.email = 'test_mail'
        self.assertEqual(str(oc), 'test_campaign: test_mail')
