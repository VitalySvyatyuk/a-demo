# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforms', '0007_tradingaccount__leverage'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradingaccount',
            name='_login',
            field=models.CharField(default=None, max_length=200, null=True, verbose_name='Login'),
        ),
    ]
