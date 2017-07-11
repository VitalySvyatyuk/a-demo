# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0003_campaign_days_after_previous_campaign'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='order_weight',
            field=models.IntegerField(default=0, help_text='Greater value will be used first when children campaign has many parent campaigns', verbose_name='Weight of campaign'),
        ),
    ]
