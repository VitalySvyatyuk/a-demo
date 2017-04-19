# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0019_auto_20151223_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='legacy_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='task',
            name='legacy_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
