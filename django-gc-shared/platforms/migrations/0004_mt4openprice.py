# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforms', '0003_auto_20161014_1802'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mt4OpenPrice',
            fields=[
                ('symbol', models.CharField(max_length=16, serialize=False, verbose_name='Symbol', primary_key=True, db_column=b'Symbol')),
                ('open_price', models.FloatField(null=True, verbose_name='Open price', db_column=b'OPEN_PRICE')),
                ('spread_digits', models.IntegerField(null=True, verbose_name='Spread digits', db_column=b'digits')),
                ('execution_type', models.IntegerField(null=True, verbose_name='Execution type', db_column=b'exemode', choices=[(1, b'instant'), (2, b'market')])),
                ('trade_status', models.IntegerField(null=True, verbose_name='Is trading allowed?', db_column=b'trade', choices=[(2, b'Trading allowed'), (1, b'No new positions allowed'), (0, b'Trading is closed')])),
            ],
            options={
                'db_table': 'OPEN_PRICE',
            },
        ),
    ]
