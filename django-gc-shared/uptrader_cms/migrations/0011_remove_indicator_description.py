# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uptrader_cms', '0010_auto_20170221_1227'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indicator',
            name='description',
        ),
    ]
