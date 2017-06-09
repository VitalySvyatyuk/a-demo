# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_personalmanager_force_tasks_full_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalmanager',
            name='can_request_new_customers',
            field=models.BooleanField(default=False, help_text='\u041c\u043e\u0436\u0435\u0442 \u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c \u043a\u043b\u0438\u0435\u043d\u0442\u043e\u0432 \u0447\u0435\u0440\u0435\u0437 \u043a\u043d\u043e\u043f\u043a\u0443 \u0432 CRM', verbose_name='\u041a\u043d\u043e\u043f\u043a\u0430'),
            preserve_default=True,
        ),
    ]
