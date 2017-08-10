from copy import copy

from django import template
from django.conf import settings
from django.template import Context
from django.test import TestCase
from massmail.models import Campaign, MessageBlock, MailingList
import fudge

from massmail.models import MessageTemplate
from project.utils import get_current_domain


class TestCampaign(TestCase):

    def test_str(self):
        c = Campaign()
        c.name = 'test_name'
        self.assertEqual(str(c), c.name)

    def test_click_count(self):
        self.assertEqual(self.campaign.click_count, 0)

    def test_count_open(self):
        self.assertEqual(self.campaign.open_count, 0)

    def test_sent_count(self):
        self.assertEqual(self.campaign.sent_count, 0)

    def test_generate_unique_token(self):
        campaign_2 = copy(self.campaign)
        campaign_2.pk = 1
        correct = '89f6ba22caba075f3e068e3b39281c5a'
        self.assertEqual(campaign_2._generate_unique_token('test'), correct)

    def test_process_html_no_netloc(self):
        self.campaign.ga_slug = True
        settings.ALLOWED_HOSTS = ['*']
        with open('django-gc-shared/massmail/tests/test_models/test_template/test.html') as html:
            ch = self.campaign.process_html(html)
        correct = '<!DOCTYPE html>\n' \
                  '<html lang="en">\n' \
                    '<head>\n' \
                        '<meta charset="UTF-8" />\n' \
                        '<a href="http://www.leningrad.spb.ru/test">Test</a>\n' \
                    '</head>\n' \
                    '<body>\n' \
                    '</body>\n' \
                  '</html>'
        self.assertEqual(ch, correct)

    def test_process_html_netloc(self):
        self.campaign.ga_slug = True
        settings.ALLOWED_HOSTS = ['www.leningrad.spb.ru']
        with open('django-gc-shared/massmail/tests/test_models/test_template/test.html') as html:
            ch = self.campaign.process_html(html, email='testmail')
        correct = '<!DOCTYPE html>\n' \
                  '<html lang="en">\n' \
                  '<head>\n' \
                  '<meta charset="UTF-8" />\n' \
                  '<a href="http://www.leningrad.spb.ru/test?utm_campaign=True&amp;campaign_id=81&amp;utm_source=email&amp;utm_medium=emailsend&amp;signature=4b2d35427b397ccf60b69362f04474aa&amp;email=testmail">Test</a>\n' \
                  '</head>\n' \
                  '<body>\n' \
                  '</body>\n' \
                  '</html>'
        self.assertTrue(set(ch).issubset(set(correct)))

    @fudge.patch('massmail.models.Campaign._get_default_context')
    def test_get_context(self, gdc):
        gdc.is_callable().returns({})
        self.campaign.personal = True
        ch = self.campaign.get_context('test_first_name', 'test_last_name', 'test_email')
        self.assertEqual(ch, {'first_name': 'test_first_name', 'last_name': 'test_last_name'})

    def test_get_absolute_url(self):
        ch = self.campaign.get_absolute_url()
        self.assertEqual(ch, u"/massmail/view/%s/" % self.campaign.pk)

    @fudge.patch('massmail.models.Campaign._get_default_context')
    def test_get_block_context(self, gdc):
        gdc.is_callable().returns({})
        mb = MessageBlock()
        mb.key = 1
        mb.value_text = 'text'
        mb.value_html = 'html'
        mb.campaign = self.campaign
        mb.save()
        correct1, correct2 = ({'1': 'text'}, {'1': 'html'})
        ch1, ch2 = self.campaign._get_block_context()
        self.assertEqual(ch1, Context(correct1))
        self.assertEqual(ch2, Context(correct2))

    @fudge.patch('massmail.models.Campaign._get_default_context')
    @fudge.patch('massmail.models.Campaign._get_block_context')
    def test_render_html(self, gdc, gbc):
        gdc.is_callable().returns(Context({'test': 'test2'}))
        gbc.is_callable().returns((1, Context({'None': True})))
        t = MessageTemplate()
        t.html = 'test_html {{ test }}'
        self.campaign.template = t
        correct = 'test_html test2'
        self.assertEqual(self.campaign.render_html(email={'test': 'email'}), correct)


    @fudge.patch('massmail.models.Campaign._get_default_context')
    @fudge.patch('massmail.models.Campaign._get_block_context')
    def test_render_text(self, gdc, gbc):
        gdc.is_callable().returns(Context({'test': 'test2'}))
        gbc.is_callable().returns((Context({'None': True}), 1))
        t = MessageTemplate()
        t.text = 'test_html {{ test }}'
        self.campaign.template = t
        correct = 'test_html test2'
        self.assertEqual(self.campaign.render_text(email={'test': 'email'}), correct)

    @fudge.patch('massmail.utils.get_unsubscribe_url')
    @fudge.patch('massmail.utils.get_unsubscribe_email')
    @fudge.patch('massmail.models.Campaign.get_absolute_url')
    def test_get_default_context(self, guu, gue, gau):
        guu.is_callable().returns('uns_url')
        gue.is_callable().returns('uns_ema')
        gau.is_callable().returns('/test')
        self.campaign.security_notification = False
        settings.MASSMAIL_UNSUBSCRIBE_EMAIL = "set@tings.ru"
        settings.EMAIL_UNSUBSCRIBE_SECRET_KEY = 12
        ch = self.campaign._get_default_context(email='somebody')
        correct = template.Context({'unsubscribe_url': 'uns_url',
                                    'domain': get_current_domain(),
                                    'subject': '',
                                    'unsubscribe_email': 'uns_ema',
                                    'browser_url': get_current_domain() + '/test',
                                    'current_site': {'domain': get_current_domain().lstrip("https://"),
                                                     }
                                    })
        self.assertEqual(ch, correct)

    @classmethod
    def setUpTestData(cls):
        cls.campaign = Campaign()
        t = MessageTemplate()
        t.save()
        cls.campaign.template = t
        cls.campaign.save()
