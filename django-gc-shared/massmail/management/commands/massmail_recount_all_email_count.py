from django.core.management import BaseCommand
from massmail.tasks import recount_all_email_count

from massmail.models import CampaignType
from profiles.models import UserProfile


class Command(BaseCommand):
    """
    Every 6 hours
    """

    def handle(self, *args, **options):
        recount_all_email_count()

        for campaign_type in CampaignType.objects.all():
                campaign_type.unsubscribed = UserProfile.objects.exclude(subscription__pk=campaign_type.pk).count()
                campaign_type.subscribed = UserProfile.objects.filter(subscription__pk=campaign_type.pk).count()
                campaign_type.save()
