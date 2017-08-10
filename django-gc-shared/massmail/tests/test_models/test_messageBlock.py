from django.test import TestCase
from massmail.models import MessageBlock, Campaign


class TestMessageBlock(TestCase):

    def test_str(self):
        c = Campaign()
        c.name = 'test_campaign'
        mb = MessageBlock()
        mb.campaign = c
        mb.key = 'test_key'
        self.assertEqual(str(mb), 'test_campaign: test_key')
