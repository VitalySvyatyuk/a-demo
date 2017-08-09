from django.test import TestCase


class TestCampaignTypeSerializer(TestCase):

    def test_import(self):
        from massmail.rest_serializers import CampaignTypeSerializer
