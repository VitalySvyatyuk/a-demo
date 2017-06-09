# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0015_auto_20151214_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='search_cache',
            field=models.CharField(default='', max_length=1024, verbose_name='\u041a\u0435\u0448 \u043f\u043e\u0438\u0441\u043a\u0430'),
        ),
    ]
