from django.test import TestCase
from massmail.models import TemplateAttachment, MessageTemplate


class TestTemplateAttachment(TestCase):

    def test_str(self):
        model = TemplateAttachment()
        template = MessageTemplate()
        template.name = 'test_template'
        model.template = template
        model.content_id = 'test'
        self.assertEqual(str(model), 'test_template: test')
