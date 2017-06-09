# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uptrader_cms', '0008_auto_20170120_1517'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='legaldocument',
            name='category',
        ),
        migrations.AddField(
            model_name='legaldocument',
            name='priority',
            field=models.IntegerField(default=0, help_text='Display order from min(first) to max (last)', verbose_name='Priority'),
        ),
    ]
