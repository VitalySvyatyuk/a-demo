# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0024_auto_20170209_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='investment_undertaking',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}),
        ),
    ]
