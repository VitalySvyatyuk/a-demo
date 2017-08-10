from django.contrib.auth.models import User
from freezegun import freeze_time
from django.core.management import call_command
from django.test import TestCase
from massmail.models import Campaign


class TestCampaignEmails(TestCase):

    # In all tests PyCharm inspections doesn't like test_func().
    # It's lambda, see setUpTestData method in the end of
    # this TestCase. In fact, we send an argument, i.e., self
    def test_emails_previous_cmp_type_all(self):
        self.campaign.previous_campaigns_type = 'all'
        self.campaign.hours_after_previous_campaign = 25
        self.assertEqual(self.test_func(), {'test@test2.us2': ('test_name_2', 'test_surname_2', 'local_context')})

    def test_emails_previous_cmp_type_none(self):
        self.campaign.previous_campaigns_type = 'none'
        self.assertEqual(self.test_func(), {})

    def test_emails_previous_cmp_type_read(self):
        self.campaign.previous_campaigns_type = 'read'
        self.campaign.hours_after_previous_campaign = 25
        self.assertEqual(self.test_func(), {'test@test2.us2': ('test_name_2', 'test_surname_2', 'local_context'),
                                            'test@test2.us3': ('test_name_2', 'test_surname_2')})

    def test_emails_previous_cmp_type_unread(self):
        self.campaign.previous_campaigns_type = 'unread'
        self.campaign.hours_after_previous_campaign = 25
        self.assertEqual(self.test_func(), {'test@test2.us3': ('test_name_2', 'test_surname_2')})

    def test_emails_previous_cmp_type_clicked(self):
        self.campaign.previous_campaigns_type = 'clicked'
        self.campaign.hours_after_previous_campaign = 25
        self.assertEqual(self.test_func(), {'test@test2.us2': ('test_name_2', 'test_surname_2', 'local_context'),
                                            'test@test2.us3': ('test_name_2', 'test_surname_2')})

    def test_emails_previous_cmp_type_unclicked(self):
        self.campaign.previous_campaigns_type = 'unclicked'
        self.campaign.hours_after_previous_campaign = 25
        self.assertEqual(self.test_func(), {'test@test2.us3': ('test_name_2', 'test_surname_2')})

    @freeze_time('2020-11-11')
    def test_emails_previous_cmp_type_unknown_no_error(self):
        User.objects.create(email='test@test2.us2', username='test2')
        User.objects.create(email='test@test2.us3', username='test3')
        self.campaign.previous_campaigns_type = None
        self.campaign.hours_after_previous_campaign = 25
        self.campaign.security_notification = True
        self.assertEqual(self.test_func(), {'tester@uptrader.us': ('test_name_2', 'test_surname_2')})

    def test_emails_previous_cmp_type_unknown_index_error(self):
        self.campaign.previous_campaigns_type = None
        self.campaign.hours_after_previous_campaign = 0.01
        self.assertEqual(self.test_func(), {})

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', 'django-shared/geobase/tests/fixtures/test_geobase.json', verbosity=0)
        call_command('loaddata', 'django-gc-shared/profiles/tests/fixtures/test_users.json', verbosity=0)
        call_command('loaddata', 'django-gc-shared/massmail/tests/test_models/test_campaign/fixtures/massmail.json', verbosity=0)
        cls.campaign = Campaign.objects.get(pk=1)
        cls.test_func = lambda x: cls.campaign._emails(
            mail_list={'test@test2.us2': ('test_name_2', 'test_surname_2', 'local_context'),
                       'test@test2.us3': ('test_name_2', 'test_surname_2'),
                       # two above should not be deleted
                       'tester@uptrader.us': ('test_name_2', 'test_surname_2'),
                       'tester@uptrader.us2': ('test_name_2', 'test_surname_2')
                       }
        )

        # mt = MessageTemplate.objects.create()
        # mt.save()
        # cls.campaign = Campaign()
        # cls.campaign.languages = ['en']
        # cls.campaign.security_notification = False
        #
        # nml = MailingList.objects.create()
        # nml.save()
        #
        # cls.campaign.template = mt
        # cls.campaign.save()  # don't remove, we need to save before manytomany assignment
        #
        # cls.camp2 = Campaign()
        # cls.camp2.template = mt
        # cls.camp2.save()
        #
        # cls.camp3 = Campaign()
        # cls.camp3.template = mt
        # cls.camp3.save()
        #
        # cls.camp4 = Campaign()
        # cls.camp4.template = mt
        # cls.camp4.save()
        #
        # cls.camp5 = Campaign()
        # cls.camp5.template = mt
        # cls.camp5.save()
        #
        # ml = MailingList.objects.create()
        # ml.subscribers_count = 2
        #
        # subs = Subscribed()
        # subs.email = 'tester@uptrader.us1'
        # subs.first_name = 'test_first_name'
        # subs.last_name = 'test_last_name'
        # subs.mailing_list = ml
        # subs.save()
        #
        # subs = Subscribed()
        # subs.email = 'tester@uptrader.us1'
        # subs.mailing_list = nml
        # subs.save()
        #
        # unsubs = Unsubscribed()
        # unsubs.email = 'tester2@uptrader.us'
        # unsubs.mailing_list = ml
        # unsubs.save()
        #
        # ml.save()
        #
        # cls.campaign.mailing_list = [ml]
        # cls.campaign.negative_mailing_list = [nml]
        # cls.campaign.previous_campaigns = [cls.camp2, cls.camp3, cls.camp4, cls.camp5]
        # cls.campaign.save()
        #
        # sm = SentMessage()
        # sm.email = 'tester@uptrader.us2'
        # sm.campaign = cls.campaign
        # sm.save()
        #
        # sm2 = SentMessage()
        # sm2.email = 'test@test2.us2'
        # sm2.campaign = cls.camp2
        # sm2.save()
        #
        # sm3 = SentMessage()
        # sm3.email = 'test@test2.us3'
        # sm3.campaign = cls.camp2
        # sm3.save()
        #
        # oc1 = OpenedCampaign()
        # oc1.campaign = cls.camp2
        # oc1.opened = True
        # oc1.email = 'test@test2.us2'
        # oc1.save()
        # oc1 = OpenedCampaign()
        # oc1.campaign = cls.camp2
        # oc1.opened = True
        # oc1.email = 'test@test2.us3'
        # oc1.save()
        #
        # oc1 = OpenedCampaign()
        # oc1.campaign = cls.camp3
        # oc1.opened = False
        # oc1.email = 'test@test2.us2'
        # oc1.save()
        # oc1 = OpenedCampaign()
        # oc1.campaign = cls.camp3
        # oc1.opened = False
        # oc1.email = 'test@test2.us3'
        # oc1.save()
        # #
        # oc1 = OpenedCampaign()
        # oc1.campaign = cls.camp4
        # oc1.opened = True
        # oc1.clicked = True
        # oc1.email = 'test@test2.us2'
        # oc1.save()
        # oc1 = OpenedCampaign()
        # oc1.campaign = cls.camp4
        # oc1.opened = True
        # oc1.clicked = True
        # oc1.email = 'test@test2.us3'
        # oc1.save()
        # #
        # oc1 = OpenedCampaign()
        # oc1.campaign = cls.camp5
        # oc1.opened = True
        # oc1.clicked = False
        # oc1.email = 'test@test2.us2'
        # oc1.save()
        # oc1 = OpenedCampaign()
        # oc1.campaign = cls.camp5
        # oc1.opened = True
        # oc1.clicked = False
        # oc1.email = 'test@test2.us3'
        # oc1.save()
        #
        # User.objects.create(email='test@test2.us2', username='test2')
        # User.objects.create(email='test@test2.us3', username='test3')
        # #
        # # oc1 = OpenedCampaign()
        # # oc1.campaign = cls.campaign
        # # oc1.opened = True
        # # oc1.opened = False
        # # oc1.save()
        #
        # cls.campaign.save()
        #
        # buf = StringIO()
        # call_command('dumpdata', 'massmail', stdout=buf)
        # buf.seek(0)
        # with open('massmail.json', 'w') as f:
        #     f.write(buf.read())

