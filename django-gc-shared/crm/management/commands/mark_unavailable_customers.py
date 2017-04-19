from django.core.management import BaseCommand

from profiles.models import UserProfile
from django.db.models import Count


class Command(BaseCommand):
    """
    Remove profiles with more than 5 failed calls from the CRM pool
    """
    def execute(self, *args, **options):
        for profile in UserProfile.objects.filter(manager__isnull=True, manager_auto_assigned=True)\
                    .annotate(Count('user__crm__calls')):
            if profile.user__crm__calls__count >= 5:
                profile.manager_auto_assigned = False
                profile.save()
