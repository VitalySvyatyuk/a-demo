# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0031_auto_20170320_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='annual_income',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Annual income (USD)', choices=[(b'over 100 000 USD', 'over 100 000'), (b'50 000 USD', b'50 000 - 100 000'), (b'10 000 USD', b'10 000 - 50 000'), (b'below 10 000 USD', 'below 10 000')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='net_capital',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Net capital (USD)', choices=[(b'over 100 000 USD', 'over 100 000'), (b'50 000 USD', b'50 000 - 100 000'), (b'10 000 USD', b'10 000 - 50 000'), (b'below 10 000 USD', 'below 10 000')]),
        ),
    ]
