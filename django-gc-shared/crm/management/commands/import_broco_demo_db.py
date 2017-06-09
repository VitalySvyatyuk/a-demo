import csv
from datetime import datetime

from django.core.management import BaseCommand

from crm.models import BrocoAccount, BrocoUser

class Command(BaseCommand):
    def execute(self, *args, **options):
        csv_reader = csv.DictReader(open("/home/valexeev/BrocoDemoDB.csv", "r"))
        for row in csv_reader:
            broco_user, created = BrocoUser.objects.get_or_create(email=row['Email'].decode('utf-8'),
                                                                  defaults={
                                                                      'has_only_demo': True,
                                                                      'manager': None,
                                                                  })
            if not created:
                continue  # We won't add demo accounts to existing Broco users, only create new ones
            for field in ("Name", "Country", "City", "State", "Address"):
                setattr(broco_user, field.lower(), row[field].decode('utf-8'))
            broco_user.phone = row["Phone"].decode('utf-8')
            broco_user.save()
            acc = BrocoAccount(mt4_id=row['Login'], user=broco_user, group="")
            try:
                creation_ts = datetime.strptime(row['Reg.date'], "%d.%m.%y %H:%M")
            except ValueError:
                try:
                    creation_ts = datetime.strptime(row['Reg.date'], "%Y.%m.%d %H:%M")
                except ValueError:
                    creation_ts = datetime.strptime(row['Reg.date'], "%d-%m-%Y")
            acc.creation_ts = creation_ts

            acc.save()

