# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0003_auto_20161015_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='duplicate_by_sms',
            field=models.BooleanField(default=False, verbose_name='\u0414\u0443\u0431\u043b\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043f\u043e SMS?'),
        ),
        migrations.AddField(
            model_name='notification',
            name='text',
            field=models.TextField(help_text='\u041c\u0430\u043a\u0441\u0438\u043c\u0443\u043c 8 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0439', null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442 SMS', blank=True),
        ),
    ]
