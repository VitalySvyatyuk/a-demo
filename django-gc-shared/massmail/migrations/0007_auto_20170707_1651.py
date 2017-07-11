# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0006_auto_20170707_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='order_weight',
            field=models.IntegerField(default=0, help_text='Lower value means this campaign trying to send first', verbose_name='Weight of campaign'),
        ),
    ]
