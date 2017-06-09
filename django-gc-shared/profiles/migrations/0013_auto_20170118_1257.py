# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0012_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='account_turnover',
            field=models.IntegerField(null=True, verbose_name='Anticipated account turnover (USD)', blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='purpose',
            field=models.CharField(max_length=1023, null=True, verbose_name='Your purpose to open an Arum capital account', blank=True),
        ),
    ]
