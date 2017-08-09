from unittest import skip

import fudge
from django.test import TestCase
from massmail.models import SmsCampaign, MailingList


class TestSmsCampaign(TestCase):

    __name__ = 'TestSmsCampaign'

    def test_str(self):
        self.assertEqual(str(self.sc), 'test_name')

    def test_sent_count(self):
        self.assertEqual(self.sc.sent_count, 0)

    def test_send_not_active(self):
        self.sc.is_active = False
        self.sc._lock = True
        self.assertEqual(self.sc.send(), None)

    def test_send_active_lock(self):
        self.sc.is_active = True
        self.sc._lock = True
        self.assertEqual(self.sc.send(), None)

    @fudge.patch('massmail.models.MailingList.get_phone_numbers')
    def test_send_no_active_lock_empty_phone_numbers(self, gpn):
        gpn.is_callable().returns(['8800'])
        self.sc.is_active = True
        self.sc._lock = False
        self.sc.send()

    def test_send_no_active_lock(self):
        self.sc.is_active = True
        self.sc._lock = False
        self.sc.send()

    @classmethod
    def setUpTestData(cls):
        cls.sc = SmsCampaign()
        cls.sc.languages = ['en']
        cls.sc.name = 'test_name'
        cls.sc.save()

        ml = MailingList.objects.create()
        cls.sc.mailing_list = [ml]
        ml.save()

        nml = MailingList.objects.create()
        cls.sc.negative_mailing_list = [nml]
        nml.save()
