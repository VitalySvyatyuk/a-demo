# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0025_auto_20160130_2318'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='close_comment',
            field=models.TextField(null=True, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439 \u043a \u0437\u0430\u043a\u0440\u044b\u0442\u0438\u044e', blank=True),
        ),
    ]
