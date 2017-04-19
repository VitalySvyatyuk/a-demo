# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0023_auto_20160129_2219'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='name_sync_from_user',
            field=models.BooleanField(default=False, verbose_name='\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u0438\u043c\u044f \u0438\u0437 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f'),
        ),
    ]
