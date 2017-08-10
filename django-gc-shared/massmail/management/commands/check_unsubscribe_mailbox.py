# -*- coding: utf-8 -*-
from email.parser import HeaderParser
from email.utils import parseaddr
import poplib
import urllib

from django.conf import settings
from django.core.management import BaseCommand
from notification import models as notification
from massmail.models import Unsubscribed, Campaign
from massmail.utils import get_email_signature
from shared.validators import email_re

from logging import getLogger
log = getLogger(__name__)


class Command(BaseCommand):
    """
    This command unsubscribes users wished to unsubscribe from mailing list.
    """

    def handle(self, *args, **options):
        """
        Command execution, no parameters are used.
        """
        log.info("Started unsibscribe command")
        log.debug("Logging to POP3 mailbox")
        mailbox = poplib.POP3_SSL(settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_POP_SERVER)
        mailbox.user(settings.MASSMAIL_UNSUBSCRIBE_EMAIL)
        n = mailbox.pass_(settings.MASSMAIL_UNSUBSCRIBE_MAILBOX_PASSWORD).split(" ")[1]

        log.info("List-unsubscribe stats: {} messages".format(n))

        # Loop over messages
        for i in range(1, int(n)+1):
            raw_message = mailbox.retr(i)[1]
            log.debug("Raw msg: {}".format(raw_message))

            msg = HeaderParser().parsestr("\n".join(raw_message))

            email_from = parseaddr(msg["From"])[1]
            email_to = parseaddr(msg["To"])[1]

            log.debug("{0} -> {1}".format(email_from, email_to))

            try:
                _, signature, campaign_id = (email_to.split("@")[0]).split("+")
            except ValueError:
                log.error("Wrong 'To' format: '%s'" % email_to)
                continue

            real_signature = get_email_signature(email_from)
            if real_signature != signature or not email_re.match(email_from):
                log.error("Signature fail: got '%s' instead of '%s'" % (signature, real_signature))
                continue
            log.debug("Signature OK")

            obj, is_created = Unsubscribed.objects.get_or_create(email=email_from)

            if is_created:
                log.debug("Unsubscibed from massmail")
                try:
                    campaign = Campaign.objects.get(id=int(campaign_id))
                except (ValueError, TypeError, Campaign.DoesNotExist):
                    log.warn("Can't find compaign by id {}".format(campaign_id))
                    pass
                else:
                    log.debug("Incrementing campaign unsubscribed")
                    campaign.unsubscribed += 1
                    campaign.save()

                    log.debug("User notification about unsubscribe")
                    notification.send([email_from], 'unsubscribed',
                                      {"email": urllib.quote(email_from), "campaign_id": campaign_id})

            log.debug("Deleting email")
            mailbox.dele(i)

        log.debug("Quiting POP3")
        mailbox.quit()
        log.info("Command finished")
