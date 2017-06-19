# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforms', '0002_auto_20160912_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradingaccount',
            name='platform_type',
            field=models.CharField(default=b'mt4', max_length=70, verbose_name='Trading platform type', choices=[(b'mt4', 'Meta Trader 4'), (b'cfh', 'CFH'), (b'strategy_store', 'Strategy Store')]),
        ),
    ]
