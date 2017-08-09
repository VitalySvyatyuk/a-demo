from django.test import TestCase
from massmail.models import Subscribed, MailingList


class TestSubscribed(TestCase):

    def test_str(self):
        s = Subscribed()
        s.mailing_list = MailingList()
        s.mailing_list.name = 'test_list'
        s.email = 'test_email'
        self.assertEqual(str(s), 'test_list (0 emails): test_email')
