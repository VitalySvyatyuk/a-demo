# -*- coding: utf-8 -*-
from email.parser import HeaderParser
from email.utils import parseaddr
import poplib
import urllib

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from notification import models as notification
from massmail.models import Unsubscribed, Campaign
from massmail.utils import get_email_signature
from shared.validators import email_re


class Command(BaseCommand):

    def execute(self, *args, **options):
        mailbox = poplib.POP3_SSL(settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_POP_SERVER)
        mailbox.user(settings.MASSMAIL_UNSUBSCRIBE_EMAIL)
        n = mailbox.pass_(settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_PASSWORD).split(" ")[1]

        print "List-unsubscribe stats:\n"
        print "%s messages\n" % n

        for i in range(1, int(n)+1):
            raw_message = mailbox.retr(i)[1]

            msg = HeaderParser().parsestr("\n".join(raw_message))

            email_from = parseaddr(msg["From"])[1]
            email_to = parseaddr(msg["To"])[1]

            print "%s -> %s" % (email_from, email_to)

            if "jobs" in email_to:  # Job emails are sent once per recipient, there's nothing to unsubscribe from,
                                    # the List-Unsubscribe header is just for compliance with mailing systems
                print "Jobs campaign, doing nothing"
                print
                continue

            try:
                _, signature, campaign_id = (email_to.split("@")[0]).split("+")
            except ValueError:
                print "wrong 'To' format: '%s'" % email_to
                print
                continue

            real_signature = get_email_signature(email_from)
            if real_signature != signature or not email_re.match(email_from):
                print "signature fail: got '%s' instead of '%s'" % (signature, real_signature)
                print
                continue
            print "signature ok"

            if campaign_id == "statement":
                for user in User.objects.filter(email=email_from):
                    for acc in user.accounts.all():
                        acc.change_mt4_field('DisableMailSend', 'all', get_or_create=True)
                    print "statements disabled"
            else:
                obj, is_created = Unsubscribed.objects.get_or_create(email=email_from)

                print "unsubscribed from massmail"

                if is_created:
                    try:
                        campaign = Campaign.objects.get(id=int(campaign_id))
                    except (ValueError, TypeError, Campaign.DoesNotExist):
                        pass
                    else:
                        campaign.unsubscribed += 1
                        campaign.save()

                        notification.send([email_from], 'unsubscribed',
                                          {"email": urllib.quote(email_from), "campaign_id": campaign_id})

            mailbox.dele(i)
            print "message deleted"
            print

        mailbox.quit()
