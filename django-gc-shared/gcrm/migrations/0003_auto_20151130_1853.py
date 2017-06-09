# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0002_auto_20151130_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='last_non_completed_task',
            field=models.ForeignKey(related_name='+', blank=True, to='gcrm.Task', null=True),
        ),
    ]
