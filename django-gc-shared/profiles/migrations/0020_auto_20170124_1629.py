# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0019_auto_20170123_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='av_transactions',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='Average volume of a transactions (USD)', choices=[(b'Less than 10 000', 'Less than 10 000'), (b'10 000 - 50 000', b'10 000 - 50 000'), (b'50 001 - 100 000', b'50 001 - 100 000'), (b'100 001 - 200 000', b'100 001 - 200 000'), (b'Over 250 000', 'Over 250 000')]),
        ),
    ]
