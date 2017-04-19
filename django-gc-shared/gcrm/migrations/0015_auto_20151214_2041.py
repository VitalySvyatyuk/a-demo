# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0014_auto_20151214_1835'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='close_comment',
        ),
        migrations.RemoveField(
            model_name='task',
            name='closed_by',
        ),
        migrations.RemoveField(
            model_name='task',
            name='status',
        ),
    ]
