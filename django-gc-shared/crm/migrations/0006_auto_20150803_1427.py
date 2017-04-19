# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_auto_20150728_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='amocontact',
            name='unsynced',
        ),
        migrations.RemoveField(
            model_name='amonote',
            name='unsynced',
        ),
        migrations.RemoveField(
            model_name='amotask',
            name='unsynced',
        ),
        migrations.AddField(
            model_name='amocontact',
            name='sync_at',
            field=models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0435\u0439 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='amonote',
            name='sync_at',
            field=models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0435\u0439 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='amotask',
            name='sync_at',
            field=models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0435\u0439 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438'),
            preserve_default=True,
        ),
    ]
