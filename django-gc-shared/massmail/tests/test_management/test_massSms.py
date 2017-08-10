from django.test import TestCase
from massmail.management.commands.send_mass_sms import Command
from massmail.models import SmsCampaign


class TestCommand(TestCase):

    def test_execute(self):
        SmsCampaign.objects.create(is_scheduled=True, _lock=False, is_sent=False,
                                                   schedule_date='2011-11-11', schedule_time='00:10:01')
        self.command.execute()

    @classmethod
    def setUpTestData(cls):
        cls.command = Command()
