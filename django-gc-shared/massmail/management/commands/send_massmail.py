# -*- coding: utf-8 -*-
from croniter import croniter
from django.core.management import BaseCommand
from datetime import datetime, timedelta
from django.db.models import Q

from massmail.models import Campaign


class Command(BaseCommand):

    def execute(self, *args, **options):

        campaigns = Campaign.objects.filter(Q(send_once=True) | Q(send_period=True), _lock=False, is_active=False)
        for campaign in campaigns:
            now = datetime.now()

            if campaign.send_once:
                send_date = campaign.send_once_datetime
            elif campaign.send_period:
                send_date = croniter(campaign.cron, now).get_next(datetime)
            else:
                continue

            # find campaigns due in 5 minutes
            if (now + timedelta(minutes=5) > send_date) and not (campaign.send_once and campaign.is_sent):
                campaign.is_active = True
                campaign.save()

        for campaign in Campaign.objects.filter(is_active=True, _lock=False):
            campaign.send()
