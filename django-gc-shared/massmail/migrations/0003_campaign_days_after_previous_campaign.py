# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0002_auto_20170524_0044'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='days_after_previous_campaign',
            field=models.IntegerField(default=0, help_text='Users which received mail from previous campaign earlier than this days will be ignored', verbose_name='Days from previous campaign'),
        ),
    ]
