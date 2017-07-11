# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0004_campaign_order_weight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='order_weight',
            field=models.IntegerField(default=0, help_text='Greater value means this campaign trying to send first', verbose_name='Weight of campaign'),
        ),
    ]
