# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalmanager',
            name='force_tasks_full_day',
            field=models.BooleanField(default=False, help_text='\u0421\u0442\u0430\u0432\u0438\u0442\u044c \u0432\u0441\u0435 \u0437\u0430\u0434\u0430\u0447\u0438 \u043f\u0440\u0438\u043d\u0443\u0434\u0438\u0442\u0435\u043b\u044c\u043d\u043e \u043d\u0430 \u0432\u0435\u0441\u044c \u0434\u0435\u043d\u044c', verbose_name='\u0417\u0430\u0434\u0430\u0447\u0438 \u043d\u0430 \u0432\u0435\u0441\u044c \u0434\u0435\u043d\u044c'),
            preserve_default=True,
        ),
    ]
