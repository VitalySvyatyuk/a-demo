# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0005_auto_20151208_2214'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='system_tags',
            field=django.contrib.postgres.fields.ArrayField(default=list, base_field=models.CharField(max_length=255), verbose_name='\u0421\u0438\u0441\u0442\u0435\u043c\u043d\u044b\u0435 \u0442\u044d\u0433\u0438', size=None),
        ),
    ]
