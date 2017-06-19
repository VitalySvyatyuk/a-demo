# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0013_task_close_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='to_complete_at',
            new_name='deadline',
        ),
    ]
