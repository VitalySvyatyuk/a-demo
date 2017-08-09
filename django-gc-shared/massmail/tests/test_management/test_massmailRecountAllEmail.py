from django.test import TestCase
from massmail.management.commands.massmail_recount_all_email_count import Command
import fudge


class TestCommand(TestCase):

    @fudge.patch('massmail.tasks.recount_all_email_count')
    def test_execute(self, f):
        f.is_callable().returns(True)
        self.command.handle()

    @classmethod
    def setUpTestData(cls):
        cls.command = Command()
