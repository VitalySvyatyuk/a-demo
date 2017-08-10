from freezegun import freeze_time
from django.test import TestCase
from massmail.management.commands.clean_bad_emails import Command
from massmail.models import Unsubscribed


class TestCommand(TestCase):

    @freeze_time('2017-07-13')
    def test_execute(self):
        Unsubscribed.objects.create(email='tester@uptrader.us')
        self.command.handle(file_name='django-gc-shared/massmail/tests/test_management/log/mail.log')

    @classmethod
    def setUpTestData(cls):
        cls.command = Command()
