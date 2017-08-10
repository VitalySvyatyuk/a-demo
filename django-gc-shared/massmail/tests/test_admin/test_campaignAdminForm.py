from datetime import timedelta, datetime
from django.utils.translation import ugettext_lazy as _
import fudge
from django.test import TestCase
from freezegun import freeze_time
from massmail.admin import CampaignAdminForm, CampaignType


class TestCampaignAdminForm(TestCase):

    def test_init(self):
        ch = CampaignAdminForm({'languages': ['en'],
                                'campaign_type': [self.ct, ]})
        correct_lang = {('en', 'English'), ('ru', 'Russian'), ('zh-cn', 'Chinese'), ('id', 'Indonesian'),
                        ('es', 'Spanish'), ('fr', 'French'), ('ar', 'Arabic'), ('ms', 'Malaysian'),
                        ('pt', 'Portuguese'), ('hi', 'Hindi')}
        self.assertTrue(isinstance(ch, CampaignAdminForm) and
                        set(ch.base_fields['languages'].choices) == correct_lang and
                        set(ch.base_fields['campaign_type'].choices) == {(self.ct.pk, 'test_CT')})

    @fudge.patch('django.forms.models.BaseModelForm.clean')
    def test_clean_once_period(self, suclean):
        suclean.is_callable().returns({'send_once': True,
                                       'send_period': True})
        ch = CampaignAdminForm({'languages': ['en'],
                                'campaign_type': [self.ct, ],
                                })
        ch.is_valid()
        ch.clean()
        self.assertEqual(ch._errors['send_once'], [_('Please choose either delayed campaign or periodical')])

    @fudge.patch('django.forms.models.BaseModelForm.clean')
    def test_clean_active_once_or_period(self, suclean):
        suclean.is_callable().returns({'is_active': True,
                                       'send_period': True,
                                       'send_once': False})
        ch = CampaignAdminForm({'languages': ['en'],
                                'campaign_type': [self.ct, ],
                                })
        ch.is_valid()
        ch.clean()
        self.assertEqual(ch._errors['is_active'], [_("Campaign can't be active and scheduled at the same time")])

    @fudge.patch('django.forms.models.BaseModelForm.clean')
    def test_clean_once_not_schedule(self, suclean):
        suclean.is_callable().returns({'send_once_datetime': False,
                                       'send_once': True})
        ch = CampaignAdminForm({'languages': ['en'],
                                'campaign_type': [self.ct, ],
                                })
        ch.is_valid()
        ch.clean()
        self.assertEqual(ch._errors['send_once_datetime'], [_('Please choose time for delayed campaign')])

    @fudge.patch('django.forms.models.BaseModelForm.clean')
    def test_clean_period_not_cron(self, suclean):
        suclean.is_callable().returns({'cron': False,
                                       'send_period': True})
        ch = CampaignAdminForm({'languages': ['en'],
                                'campaign_type': [self.ct, ],
                                })
        ch.is_valid()
        ch.clean()
        self.assertEqual(ch._errors['cron'], [_("Please specify schedule for the campaign")])

    @freeze_time('2017-10-10')
    @fudge.patch('django.forms.models.BaseModelForm.clean')
    def test_clean_once_schedule_less_now(self, suclean):
        suclean.is_callable().returns({'send_once': True,
                                       'send_once_datetime': datetime.now() - timedelta(5),
                                       'cron': True})

        ch = CampaignAdminForm({'languages': ['en'],
                                'campaign_type': [self.ct, ],
                                })
        ch.is_valid()
        ch.clean()
        self.assertEqual(ch._errors['send_once_datetime'], [_('This date has already passed')])

    @classmethod
    def setUpTestData(cls):
        cls.ct = CampaignType()
        cls.ct.title = 'test_CT'
        cls.ct.save()
