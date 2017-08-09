from django.test import TestCase
from massmail.models import CampaignType


class TestCampaignType(TestCase):

    def test_str(self):
        c = CampaignType()
        c.title = 'test_title'
        self.assertEqual(str(c), c.title)
