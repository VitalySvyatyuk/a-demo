from django.test import TestCase
from massmail.apps import MassmailConfig
from notification.models import NotificationTypesRegister


class TestMassmailConfig(TestCase):

    def test_ready(self):
        self.assertEqual(self.config.name, 'massmail')
        self.assertTrue(('unsubscribed', 'Unsubscribed from emails') in
                        NotificationTypesRegister.notification_types)

    @classmethod
    def setUpTestData(cls):
        import massmail
        cls.config = MassmailConfig(app_module=massmail, app_name='massmail')
