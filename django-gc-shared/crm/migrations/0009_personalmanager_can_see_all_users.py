# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0008_auto_20150804_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalmanager',
            name='can_see_all_users',
            field=models.BooleanField(default=False, verbose_name='\u041c\u043e\u0436\u0435\u0442 \u0432\u0438\u0434\u0435\u0442\u044c \u0432\u0441\u0435\u0445 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439'),
        ),
    ]
