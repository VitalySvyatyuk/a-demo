from django.core.management import BaseCommand
from datetime import datetime

from massmail.models import SmsCampaign

class Command(BaseCommand):

    def execute(self, *args, **options):

        # for scheduled compaings
        for campaign in SmsCampaign.objects.filter(is_scheduled=True, _lock=False, is_sent=False,
                                                schedule_date__isnull=False, schedule_time__isnull=False):
            sceddate = datetime.combine(campaign.schedule_date, campaign.schedule_time)
            nowdate = datetime.today()
            if sceddate < nowdate:
                campaign.is_active = True
                campaign.save()

        for campaign in SmsCampaign.objects.filter(is_active=True, _lock=False):
            campaign.send()
