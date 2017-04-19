# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0025_userprofile_investment_undertaking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='derivative_instruments',
            field=django_hstore.fields.DictionaryField(default={}),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='forex_instruments',
            field=django_hstore.fields.DictionaryField(default={}),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='investment_undertaking',
            field=django_hstore.fields.DictionaryField(default={}),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='transferable_securities',
            field=django_hstore.fields.DictionaryField(default={}),
        ),
    ]
