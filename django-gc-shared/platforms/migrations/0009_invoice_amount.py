# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforms', '0008_tradingaccount__login'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradingaccount',
            name='invoice_amount',
            field=models.PositiveIntegerField(default=1, verbose_name="Invoice amount"),
        ),
    ]
