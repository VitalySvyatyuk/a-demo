# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import annoying.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0004_auto_20151130_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='info',
            field=annoying.fields.JSONField(default=list, verbose_name='\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u043d\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f'),
        ),
    ]
