from django.contrib.admin import AdminSite
from django.test import TestCase
from massmail.admin import SmsCampaignAdmin
import fudge

from massmail.models import SmsCampaign


class TestSmsCampaignAdmin(TestCase):

    def test_sent_count(self):
        self.assertEqual(self.admin.sent_count(self.f), 2)

    @classmethod
    def setUpTestData(cls):
        cls.admin = SmsCampaignAdmin(admin_site=AdminSite(), model=SmsCampaign)
        cls.f = fudge.Fake()
        cls.f.sent_count = 2
