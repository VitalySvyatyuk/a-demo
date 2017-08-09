from django.test import TestCase


class TestCampaignTypeViewSet(TestCase):

    def test_import(self):
        from massmail.rest_api import CampaignTypeViewSet
