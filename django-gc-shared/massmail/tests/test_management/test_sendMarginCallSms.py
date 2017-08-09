from unittest import skip

from django.test import TestCase
from massmail.management.commands.send_margin_call_sms import Command


class TestCommand(TestCase):

    @skip  # FIXME: need mt4 app to test this
    def test_handle(self):
        self.command.handle()

    @classmethod
    @skip
    def setUpTestData(cls):
        cls.command = Command()
