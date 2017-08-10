from django.test import TestCase
from massmail.admin import MessageBlockAdminForm


class TestMessageBlockAdminForm(TestCase):

    def test_init(self):
        ch = MessageBlockAdminForm({'value_html': 'test'})
        ch.is_valid()
        self.assertTrue(isinstance(ch, MessageBlockAdminForm) and ch.cleaned_data['value_html'] == 'test')
