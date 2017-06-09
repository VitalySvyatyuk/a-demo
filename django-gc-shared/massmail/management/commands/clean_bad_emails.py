# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from re import search

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from massmail.models import Unsubscribed


class Command(BaseCommand):

    def execute(self, *args, **options):

        f = open("/var/log/mail.log", "r")

        yesterday = (datetime.now() - timedelta(1)).strftime("%b %e")

        emails = set()

        # pass today's records
        for l in f:
            if l.startswith(yesterday):
                break

        for l in f:
            # quit, if we reached day before yesterday
            if not l.startswith(yesterday):
                break

            if (
                "550 Message was not accepted -- invalid mailbox" in l  # mail.ru
                or "550 5.7.1 No such user!" in l  # yandex error
                or "550-5.1.1 The email account that you tried to reach does not exist" in l  # gmail
                or "Recipient address rejected: user not found" in l  # rambler
            ):
                match = search("to=<([^>]+)>", l)

                if match:
                    emails.add(match.group(1))

        f.close()

        for email in emails:
            for user in User.objects.filter(email=email):
                Unsubscribed.objects.get_or_create(email=email)

                for acc in user.accounts.all():
                    acc.change_mt4_field('DisableMailSend', 'all', get_or_create=True)
