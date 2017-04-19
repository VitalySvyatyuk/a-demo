# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0015_auto_20170118_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='risk_appetite',
            field=models.BooleanField(default=False),
        ),
    ]
