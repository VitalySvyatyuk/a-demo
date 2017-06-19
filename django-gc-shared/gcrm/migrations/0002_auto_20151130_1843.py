# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='created_at',
            new_name='creation_ts',
        ),
        migrations.RenameField(
            model_name='note',
            old_name='created_at',
            new_name='creation_ts',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='note',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='contact',
            name='update_ts',
            field=models.DateTimeField(default=None, verbose_name='\u0414\u0430\u0442\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f', auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='note',
            name='update_ts',
            field=models.DateTimeField(default=None, verbose_name='\u0414\u0430\u0442\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f', auto_now=True),
            preserve_default=False,
        ),
    ]
