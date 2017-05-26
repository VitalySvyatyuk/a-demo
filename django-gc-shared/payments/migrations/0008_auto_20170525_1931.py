# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0007_auto_20170215_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmethod',
            name='max_commission',
            field=models.CharField(default='', max_length=150, verbose_name='Max commision', blank=True),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='min_commission',
            field=models.CharField(default='', max_length=150, verbose_name='Min commision', blank=True),
        ),
    ]
