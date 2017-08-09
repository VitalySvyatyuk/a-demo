from django.test import TestCase
from massmail.models import SentSms, SmsCampaign


class TestSentSms(TestCase):

    def test_str(self):
        sms = SentSms()
        campaign = SmsCampaign()
        campaign.name = 'campaign'
        sms.campaign = campaign
        sms.phone_number = '89523812603'
        self.assertEqual(str(sms), 'campaign: 89523812603')
