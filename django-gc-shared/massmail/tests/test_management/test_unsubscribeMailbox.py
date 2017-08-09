import fudge
from django.conf import settings
from django.test import TestCase
from massmail.management.commands.check_unsubscribe_mailbox import Command
from massmail.models import Campaign, MessageTemplate


class TestCommand(TestCase):

    @fudge.patch('poplib.POP3_SSL')
    def test_execute_ok_campaign_id_statement(self, pop3):
        raw_message = [1, """MIME-Version: 1.0
Received: by 10.229.233.76 with HTTP; Sat, 2 Jul 2011 04:30:31 -0700 (PDT)
Date: Sat, 2 Jul 2011 13:30:31 +0200
Delivered-To: alain.spineux@gmail.com
Message-ID: <CAAJL_=kPAJZ=fryb21wBOALp8-XOEL-h9j84s3SjpXYQjN3Z3A@mail.gmail.com>
Subject: =?ISO-8859-1?Q?Dr.=20Pointcarr=E9?=
From: Alain Spineux <tester@uptrader.us>
To: =?ISO-8859-1?Q?Dr=2E_Pointcarr=E9?= <alain+8d4ba54ed7604ef0983175135d73562617dd2120+statement@gmail.com>
Content-Type: multipart/alternative; boundary=000e0cd68f223dea3904a714768b
"""]
        mailbox = fudge.Fake()\
            .expects('user').returns('response')\
            .expects('pass_').returns('test 1')\
            .expects('retr').returns(raw_message)\
            .provides('dele').returns(True)\
            .expects('quit').returns(True)
        pop3.is_callable().returns(mailbox)
        settings.EMAIL_UNSUBSCRIBE_SECRET_KEY = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_POP_SERVER = ''
        settings.MASSMAIL_UNSUBSCRIBE_EMAIL = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_PASSWORD = 'test password'
        self.command.handle()

    @fudge.patch('poplib.POP3_SSL')
    def test_execute_ok_campaign_id_ok(self, pop3):
        mt = MessageTemplate()
        mt.save()
        c = Campaign()
        c.template = mt
        c.save()
        print(Campaign.objects.all())

        raw_message = [1, """MIME-Version: 1.0
Received: by 10.229.233.76 with HTTP; Sat, 2 Jul 2011 04:30:31 -0700 (PDT)
Date: Sat, 2 Jul 2011 13:30:31 +0200
Delivered-To: alain.spineux@gmail.com
Message-ID: <CAAJL_=kPAJZ=fryb21wBOALp8-XOEL-h9j84s3SjpXYQjN3Z3A@mail.gmail.com>
Subject: =?ISO-8859-1?Q?Dr.=20Pointcarr=E9?=
From: Alain Spineux <tester@uptrader.us>
To: =?ISO-8859-1?Q?Dr=2E_Pointcarr=E9?= <alain+8d4ba54ed7604ef0983175135d73562617dd2120+%s@gmail.com>
Content-Type: multipart/alternative; boundary=000e0cd68f223dea3904a714768b
""" % c.pk]
        mailbox = fudge.Fake() \
            .expects('user').returns('response') \
            .expects('pass_').returns('test 1') \
            .expects('retr').returns(raw_message) \
            .provides('dele').returns(True) \
            .expects('quit').returns(True)
        pop3.is_callable().returns(mailbox)
        settings.EMAIL_UNSUBSCRIBE_SECRET_KEY = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_POP_SERVER = ''
        settings.MASSMAIL_UNSUBSCRIBE_EMAIL = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_PASSWORD = 'test password'
        self.command.handle()

    @fudge.patch('poplib.POP3_SSL')
    def test_execute_ok_campaign_id_unexisting(self, pop3):
        raw_message = [1, """MIME-Version: 1.0
Received: by 10.229.233.76 with HTTP; Sat, 2 Jul 2011 04:30:31 -0700 (PDT)
Date: Sat, 2 Jul 2011 13:30:31 +0200
Delivered-To: alain.spineux@gmail.com
Message-ID: <CAAJL_=kPAJZ=fryb21wBOALp8-XOEL-h9j84s3SjpXYQjN3Z3A@mail.gmail.com>
Subject: =?ISO-8859-1?Q?Dr.=20Pointcarr=E9?=
From: Alain Spineux <tester@uptrader.us>
To: =?ISO-8859-1?Q?Dr=2E_Pointcarr=E9?= <alain+8d4ba54ed7604ef0983175135d73562617dd2120+0@gmail.com>
Content-Type: multipart/alternative; boundary=000e0cd68f223dea3904a714768b
"""]
        mailbox = fudge.Fake() \
            .expects('user').returns('response') \
            .expects('pass_').returns('test 1') \
            .expects('retr').returns(raw_message) \
            .provides('dele').returns(True) \
            .expects('quit').returns(True)
        pop3.is_callable().returns(mailbox)
        settings.EMAIL_UNSUBSCRIBE_SECRET_KEY = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_POP_SERVER = ''
        settings.MASSMAIL_UNSUBSCRIBE_EMAIL = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_PASSWORD = 'test password'
        self.command.handle()

    @fudge.patch('poplib.POP3_SSL')
    def test_execute_bad_signature(self, pop3):
        raw_message = [1, """MIME-Version: 1.0
Received: by 10.229.233.76 with HTTP; Sat, 2 Jul 2011 04:30:31 -0700 (PDT)
Date: Sat, 2 Jul 2011 13:30:31 +0200
Delivered-To: alain.spineux@gmail.com
Message-ID: <CAAJL_=kPAJZ=fryb21wBOALp8-XOEL-h9j84s3SjpXYQjN3Z3A@mail.gmail.com>
Subject: =?ISO-8859-1?Q?Dr.=20Pointcarr=E9?=
From: Alain Spineux <alain.spineux@gmail.com>
To: =?ISO-8859-1?Q?Dr=2E_Pointcarr=E9?= <alain+BAD_SIGNATURE+11@gmail.com>
Content-Type: multipart/alternative; boundary=000e0cd68f223dea3904a714768b
"""]
        mailbox = fudge.Fake() \
            .expects('user').returns('response') \
            .expects('pass_').returns('test 1') \
            .expects('retr').returns(raw_message) \
            .provides('dele').returns(True) \
            .expects('quit').returns(True)
        pop3.is_callable().returns(mailbox)
        settings.EMAIL_UNSUBSCRIBE_SECRET_KEY = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_POP_SERVER = ''
        settings.MASSMAIL_UNSUBSCRIBE_EMAIL = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_PASSWORD = 'test password'
        self.command.handle()

    @fudge.patch('poplib.POP3_SSL')
    def test_execute_with_jobs(self, pop3):
        raw_message = [1, """MIME-Version: 1.0
Received: by 10.229.233.76 with HTTP; Sat, 2 Jul 2011 04:30:31 -0700 (PDT)
Date: Sat, 2 Jul 2011 13:30:31 +0200
Delivered-To: alain.spineux@gmail.com
Message-ID: <CAAJL_=kPAJZ=fryb21wBOALp8-XOEL-h9j84s3SjpXYQjN3Z3A@mail.gmail.com>
Subject: =?ISO-8859-1?Q?Dr.=20Pointcarr=E9?=
From: Alain Spineux <alain.spineux@gmail.com>
To: =?ISO-8859-1?Q?Dr=2E_Pointcarr=E9?= <jobs+1+11@gmail.com>
Content-Type: multipart/alternative; boundary=000e0cd68f223dea3904a714768b
"""]
        mailbox = fudge.Fake()\
            .expects('user').returns('response')\
            .expects('pass_').returns('test 1')\
            .expects('retr').returns(raw_message)\
            .provides('dele').returns(True)\
            .expects('quit').returns(True)
        pop3.is_callable().returns(mailbox)
        settings.EMAIL_UNSUBSCRIBE_SECRET_KEY = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_POP_SERVER = ''
        settings.MASSMAIL_UNSUBSCRIBE_EMAIL = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_PASSWORD = 'test password'
        self.command.handle()

    @fudge.patch('poplib.POP3_SSL')
    def test_execute_wrong_format(self, pop3):
        raw_message = [1, """MIME-Version: 1.0
    Received: by 10.229.233.76 with HTTP; Sat, 2 Jul 2011 04:30:31 -0700 (PDT)
    Date: Sat, 2 Jul 2011 13:30:31 +0200
    Delivered-To: alain.spineux@gmail.com
    Message-ID: <CAAJL_=kPAJZ=fryb21wBOALp8-XOEL-h9j84s3SjpXYQjN3Z3A@mail.gmail.com>
    Subject: =?ISO-8859-1?Q?Dr.=20Pointcarr=E9?=
    From: Alain Spineux <alain.spineux@gmail.com>
    To: =?ISO-8859-1?Q?Dr=2E_Pointcarr=E9?= <jobs+1+11@gmail.com>
    Content-Type: multipart/alternative; boundary=000e0cd68f223dea3904a714768b
    """]
        mailbox = fudge.Fake() \
            .expects('user').returns('response') \
            .expects('pass_').returns('test 1') \
            .expects('retr').returns(raw_message) \
            .provides('dele').returns(True) \
            .expects('quit').returns(True)
        pop3.is_callable().returns(mailbox)
        settings.EMAIL_UNSUBSCRIBE_SECRET_KEY = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_POP_SERVER = ''
        settings.MASSMAIL_UNSUBSCRIBE_EMAIL = ''
        settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_PASSWORD = 'test password'
        self.command.handle()

    @classmethod
    def setUpTestData(cls):
        cls.command = Command()
