# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0012_subsribed_campaigntype'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscribed',
            name='phone',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
