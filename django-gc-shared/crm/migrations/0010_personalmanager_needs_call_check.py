# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0009_personalmanager_can_see_all_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalmanager',
            name='needs_call_check',
            field=models.BooleanField(default=True, help_text='\u041f\u0435\u0440\u0435\u0434 \u043f\u043e\u043b\u0443\u0447\u0435\u043d\u0438\u0435\u043c \u043d\u043e\u0432\u043e\u0433\u043e \u043a\u043b\u0438\u0435\u043d\u0442\u0430, \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0442\u044c \u043d\u0430\u043b\u0438\u0447\u0438\u0435 \u0437\u0432\u043e\u043d\u043a\u0430 \u043f\u0440\u0435\u0434\u044b\u0434\u0443\u0449\u0435\u043c\u0443', verbose_name='\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0437\u0432\u043e\u043d\u043a\u043e\u0432'),
        ),
    ]
