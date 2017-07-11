# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0007_auto_20170707_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='previous_campaigns',
            field=models.ManyToManyField(help_text=b'Just ctrl+click to previous campaign ', related_name='_campaign_previous_campaigns_+', null=True, to='massmail.Campaign', blank=True),
        ),
    ]
