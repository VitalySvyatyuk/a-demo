# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referral', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountverification',
            name='account',
        ),
        migrations.DeleteModel(
            name='AccountVerification',
        ),
    ]
