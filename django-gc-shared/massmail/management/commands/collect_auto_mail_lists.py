# -*- coding: utf-8 -*-
from django.core.management import BaseCommand

from massmail.auto_mail import BaseMarketingCampaign


class Command(BaseCommand):
    def handle(self, *args, **options):
        BaseMarketingCampaign.collect_all()