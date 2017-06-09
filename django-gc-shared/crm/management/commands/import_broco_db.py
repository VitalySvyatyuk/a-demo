import csv
from datetime import datetime

from django.core.management import BaseCommand

from crm.models import BrocoAccount, BrocoUser


class Command(BaseCommand):
    def execute(self, *args, **options):
        csv_reader = csv.DictReader(open("/home/valexeev/BrocoDB.csv", "r"))
        for row in csv_reader:
            broco_user = BrocoUser.objects.get_or_create(email=row['Email'].decode('utf-8'))[0]
            for field in ("Name", "Country", "City", "State", "Address"):
                if not getattr(broco_user, field.lower()):
                    setattr(broco_user, field.lower(), row[field].decode('utf-8'))
            phone = row["Phone"].decode('utf-8')
            if phone not in broco_user.phone:
                if broco_user.phone:
                    broco_user.phone += u"; " + phone
                else:
                    broco_user.phone = phone
            broco_user.save()
            acc = BrocoAccount(mt4_id=row['Login'], user=broco_user, group=row['Group'])
            try:
                creation_ts = datetime.strptime(row['Reg.date'], "%d.%m.%y %H:%M")
            except ValueError:
                creation_ts = datetime.strptime(row['Reg.date'], "%Y.%m.%d %H:%M")
            acc.creation_ts = creation_ts

            acc.save()

