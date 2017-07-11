# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0009_auto_20170707_1702'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='days_after_previous_campaign',
        ),
        migrations.AddField(
            model_name='campaign',
            name='hours_after_previous_campaign',
            field=models.IntegerField(default=0, help_text='Users which received mail from previous campaign earlier than this hours will be ignored', verbose_name='Hours from previous campaign'),
        ),
    ]
