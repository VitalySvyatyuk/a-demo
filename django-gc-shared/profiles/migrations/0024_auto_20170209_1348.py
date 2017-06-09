# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0023_auto_20170202_1626'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='av_transactions',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='education_level',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='fr_transactions',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='pass_seminar',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='risk_appetite',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='trade_years',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='traded_forex',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='derivative_instruments',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='forex_instruments',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='transferable_securities',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}),
        ),
    ]
