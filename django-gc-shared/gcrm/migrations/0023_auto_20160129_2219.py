# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0022_contactuserviewrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='assigned_ts',
            field=models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0438 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0430'),
        ),
        migrations.AddField(
            model_name='contact',
            name='is_assigned_by_button',
            field=models.BooleanField(default=False, verbose_name='\u0412\u0437\u044f\u0442 \u043f\u043e \u043a\u043d\u043e\u043f\u043a\u0435'),
        ),
    ]
