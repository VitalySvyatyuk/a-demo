import fudge
from django.conf import settings
from django.test import TestCase
from massmail.utils import get_signature, get_unsubscribe_email, get_email_signature, get_unsubscribe_url


class TestUtils(TestCase):

    def test_get_signature(self):
        correct = 'b09740944fb0122af760eb905c8f1bec'
        self.assertEqual(get_signature('test@email.ru'), correct)

    @fudge.patch('massmail.utils.get_email_signature')
    def test_get_unsubscribe_email(self, gs):
        gs.is_callable().returns('fce453586d92aac01424130a23762f89')
        settings.MASSMAIL_UNSUBSCRIBE_EMAIL = 'massmail@test.test'
        settings.EMAIL_UNSUBSCRIBE_SECRET_KEY = '1'
        self.assertEqual(get_unsubscribe_email('test@email.ru', 1),
                         'massmail+fce453586d92aac01424130a23762f89+1@test.test')

    def test_get_email_signature(self):
        settings.MASSMAIL_UNSUBSCRIBE_EMAIL = 'massmail@test.test'
        settings.EMAIL_UNSUBSCRIBE_SECRET_KEY = '1'
        self.assertEqual(get_email_signature('test@email.ru'), 'fc6bbaf16e52d8235b356557c913ee8016ef1365')

    @fudge.patch('massmail.utils.get_signature')
    def test_get_unsubscribe_url(self, gs):
        gs.is_callable().returns('fce453586d92aac01424130a23762f89')
        self.assertEqual(get_unsubscribe_url('test@email.ru', 1),
                         'https://ru.arumcapital.eu/my/massmail/unsubscribe_user'
                         '/fce453586d92aac01424130a23762f89/test%2540email.ru')


