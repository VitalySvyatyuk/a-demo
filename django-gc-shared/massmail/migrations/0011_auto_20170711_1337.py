# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0010_auto_20170710_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='hours_after_previous_campaign',
            field=models.FloatField(default=0, help_text='Users which received mail from previous campaign earlier than this hours will be ignored', verbose_name='Hours from previous campaign'),
        ),
    ]
