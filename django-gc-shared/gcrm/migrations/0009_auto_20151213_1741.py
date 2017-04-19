# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0008_auto_20151212_2050'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='author',
        ),
        migrations.RemoveField(
            model_name='note',
            name='contact',
        ),
        migrations.RemoveField(
            model_name='task',
            name='assignee',
        ),
        migrations.RemoveField(
            model_name='task',
            name='note_ptr',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='last_non_completed_task',
        ),
        migrations.DeleteModel(
            name='Note',
        ),
        migrations.DeleteModel(
            name='Task',
        ),
    ]
