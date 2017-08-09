from django.core.mail import EmailMultiAlternatives
from django.test import TestCase
from massmail.models import MessageTemplate
from django.template import Context


class TestMessageTemplate(TestCase):

    def test_str(self):
        self.assertEqual(str(self.template), self.template.name)

    def test_render_html(self):
        self.assertEqual(self.template.render_html(Context({'s': 'succeed'})), 'test_html succeed')

    def test_render_text(self):
        self.assertEqual(self.template.render_text(Context({'s': 'succeed'})), 'test_text succeed')

    def test_create_email_with_txt_html(self):
        ch = self.template.create_email(reply_to='8800',
                                        msgtype='letter',
                                        context={'unsubscribe_email': 'email_un',
                                                 'unsubscribe_url': 'url_un'},
                                        connection=True)
        self.assertTrue(isinstance(ch, EmailMultiAlternatives))

    def test_create_email_no_txt_html(self):
        template = MessageTemplate()
        template.name = 'test_template'
        ch = template.create_email(reply_to='8800',
                                   msgtype='letter',
                                   context={'unsubscribe_email': 'email_un',
                                            'unsubscribe_url': 'url_un'},
                                   connection=True,
                                   email_to='email_to')
        self.assertTrue(isinstance(ch, EmailMultiAlternatives))

    @classmethod
    def setUpTestData(cls):
        cls.template = MessageTemplate()
        cls.template.name = 'test_template'
        cls.template.html = 'test_html {{ s }}'
        cls.template.text = 'test_text {{ s }}'
