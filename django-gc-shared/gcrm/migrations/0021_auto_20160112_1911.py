# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0020_auto_20160111_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='search_cache',
            field=models.TextField(default='', verbose_name='\u041a\u0435\u0448 \u043f\u043e\u0438\u0441\u043a\u0430'),
        ),
    ]
