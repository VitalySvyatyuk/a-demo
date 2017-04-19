# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforms', '0006_changequote'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradingaccount',
            name='_leverage',
            field=models.IntegerField(default=50, verbose_name='Account leverage'),
        ),
    ]
