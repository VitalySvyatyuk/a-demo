# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0011_auto_20170711_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaigntype',
            name='subscribed',
            field=models.PositiveIntegerField(default=0, verbose_name='Subscribed'),
        ),
    ]
