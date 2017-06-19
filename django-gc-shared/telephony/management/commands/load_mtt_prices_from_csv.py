# coding=utf-8
import csv
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from telephony.models import CallDetailRecord


class Command(BaseCommand):
    args = '<path to csv>'
    help = 'Loads prices of MTT calls from their CSV statement'

    def handle(self, *args, **options):
        infile = open(args[0], 'rb')
        reader = csv.reader(infile, delimiter=";")
        for row in reader:
            if len(row) == 11:
                date, phone, price = datetime.strptime(row[0], "%d.%m.%y %H:%M:%S"), row[4], Decimal(row[9])
                calls = CallDetailRecord.objects.filter(
                    number_b=phone,
                    call_date__gte=date - timedelta(seconds=30),
                    call_date__lte=date + timedelta(seconds=30),
                    disposition="ANSWERED",
                )
                if calls:
                    call = calls[0]
                    if not call.price:
                        call.price = price
                        call.save()