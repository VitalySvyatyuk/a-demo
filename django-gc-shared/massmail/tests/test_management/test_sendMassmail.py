from datetime import datetime, timedelta
import fudge
from freezegun import freeze_time
from django.test import TestCase
from massmail.management.commands.send_massmail import Command
from massmail.models import Campaign, MessageTemplate


class TestCommand(TestCase):

    @freeze_time('2017-10-10')
    def test_execute_send_once(self):
        mt = MessageTemplate()
        mt.save()
        Campaign.objects.create(template=mt, send_once=True, send_period=False,
                                _lock=False, is_active=False, send_once_datetime='2017-10-9', is_sent=False)
        self.command.execute()

    @fudge.patch('croniter.croniter')
    @freeze_time('2017-10-10')
    def test_execute_send_period(self, cron):
        f = fudge.Fake()
        f.get_next = lambda x: datetime.now() - timedelta(days=2)
        cron.is_callable().returns(f)
        mt = MessageTemplate()
        mt.save()
        Campaign.objects.create(template=mt, send_once=False, send_period=True, _lock=False, is_active=False)
        self.command.execute()

    @classmethod
    def setUpTestData(cls):
        cls.command = Command()
