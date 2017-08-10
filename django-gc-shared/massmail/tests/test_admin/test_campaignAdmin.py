from django.contrib.admin import AdminSite
from django.test import TestCase
from massmail.admin import CampaignAdmin
from massmail.models import Campaign
import fudge


class TestCampaignAdmin(TestCase):

    def test_open_count(self):
        self.assertEqual(self.admin.open_count(self.f), 1)

    def test_click_count(self):
        self.assertEqual(self.admin.click_count(self.f), 2)

    @classmethod
    def setUpTestData(cls):
        cls.admin = CampaignAdmin(admin_site=AdminSite(), model=Campaign)
        cls.f = fudge.Fake()
        cls.f.open_count = 1
        cls.f.click_count = 2
