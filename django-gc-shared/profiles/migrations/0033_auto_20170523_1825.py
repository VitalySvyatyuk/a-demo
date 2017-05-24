# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0032_auto_20170321_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='annual_income',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Annual income (USD)', choices=[(b'> 100000', 'over 100 000'), (b'50000 - 100000', b'50 000 - 100 000'), (b'10000 - 50000', b'10 000 - 50 000'), (b'< 10000', 'below 10 000')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='financial_commitments',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='Monthly financial commitments', choices=[(b'< 20%', 'Less than 20%'), (b'21% - 40%', b'21% - 40%'), (b'41% - 60%', b'41% - 60%'), (b'61% - 80%', b'61% - 80%'), (b'> 80%', 'Over 80%')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='net_capital',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Net capital (USD)', choices=[(b'> 100000', 'over 100 000'), (b'50000 - 100000', b'50 000 - 100 000'), (b'10000 - 50000', b'10 000 - 50 000'), (b'< 10000', 'below 10 000')]),
        ),
    ]
