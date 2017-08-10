# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.test import TestCase
from massmail.admin import SmsCampaignAdminForm


class TestSmsCampaignAdminForm(TestCase):

    def test_init(self):
        ch = SmsCampaignAdminForm({'text': 'test',
                                   'languages': ['en', ]})
        ch.is_valid()
        self.assertTrue(isinstance(ch, SmsCampaignAdminForm) and
                        ch.cleaned_data['text'] == 'test')

    def test_clean_ok(self):
        ch = SmsCampaignAdminForm({'text': 'test_data',
                                   'languages': ['en', ]})
        ch.is_valid()
        ch.clean()
        self.assertTrue(isinstance(ch, SmsCampaignAdminForm) and
                        ch.cleaned_data['text'] == 'test_data')

    def test_clean_decode_error_len_less(self):
        ch = SmsCampaignAdminForm({'text': u'¡',
                                   'languages': ['en', ]})
        ch.is_valid()
        ch.clean()
        self.assertTrue(isinstance(ch, SmsCampaignAdminForm) and
                        ch.cleaned_data['text'] == u'¡')

    def test_clean_too_long(self):
        s1 = 'a'.join(str(x) for x in range(555))
        ch = SmsCampaignAdminForm({'text': s1,
                                   'languages': ['en', ]})
        ch.is_valid()
        ch.clean()
        self.assertTrue(isinstance(ch, SmsCampaignAdminForm) and
                        ch.cleaned_data['text'] == s1 and
                        ch.errors['text'] == [_('Message length exceeds the maximum length')])
