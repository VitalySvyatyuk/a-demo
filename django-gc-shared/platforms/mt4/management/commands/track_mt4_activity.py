# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.core.management import BaseCommand

from platforms.mt4.external.models import RealUser
from profiles.models import UserProfile


class Command(BaseCommand):
    def handle(self, **options):
        for mt4_id, lastdate in RealUser.objects.filter(lastdate__gte=datetime.now()-timedelta(hours=6)).values_list('login', 'lastdate'):
            UserProfile.objects.filter(user__accounts__mt4_id=mt4_id).add_last_activity('MT4', 'contains', lastdate)
