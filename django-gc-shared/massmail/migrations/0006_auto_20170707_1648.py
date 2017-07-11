# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0005_auto_20170707_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='previous_campaigns',
            field=models.ManyToManyField(related_name='_campaign_previous_campaigns_+', null=True, verbose_name=b'trigger chain campaigns', to='massmail.Campaign', blank=True),
        ),
    ]
