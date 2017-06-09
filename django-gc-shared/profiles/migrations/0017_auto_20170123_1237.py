# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0016_userprofile_risk_appetite'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='first_name_ru',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='last_name_ru',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='middle_name_ru',
        ),
    ]
