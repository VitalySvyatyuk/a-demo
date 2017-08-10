# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from re import search

from django.core.management import BaseCommand
from massmail.models import Unsubscribed

from logging import getLogger
log = getLogger(__name__)


class Command(BaseCommand):
    """
    This command drops unavailable users from subscriptions.
    Supposed to be run daily.
    """

    def handle(self, *args, **options):
        """
        Command execution.
        :param args: not used
        :param options:
            file_name - path to mail.log
        """

        log.info("Started email clean command")
        log.debug("Opening file")
        fname = options.pop('file_name', "/var/log/mail.log")
        f = open(fname, "r")

        yesterday = (datetime.now() - timedelta(1)).strftime("%b %e")
        log.debug("Yesterday was {}".format(yesterday))

        emails = set()

        log.debug("Skipping lines until yesterday")
        for l in f:
            if l.startswith(yesterday):
                break

        log.debug("Processing")
        for l in f:
            if not l.startswith(yesterday):
                log.debug("Reached this day, stopped parsing")
                break

            # Error templates
            if (
                "550 Message was not accepted -- invalid mailbox" in l  # mail.ru
                or "550 5.7.1 No such user!" in l  # yandex error
                or "550-5.1.1 The email account that you tried to reach does not exist" in l  # gmail
                or "Recipient address rejected: user not found" in l  # rambler
            ):
                match = search("to=<([^>]+)>", l)

                if match:
                    log.debug("Bad mail: {}".format(match.group(1)))
                    emails.add(match.group(1))

        log.debug("Closing mail log")
        f.close()

        log.info("{} bad emails found, unsubscribing them".format(len(emails)))
        for email in emails:
            log.debug("Unsubscribing {}".format(email))
            Unsubscribed.objects.get_or_create(email=email)

