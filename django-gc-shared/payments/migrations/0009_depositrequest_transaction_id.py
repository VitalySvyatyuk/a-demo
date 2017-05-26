# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0008_auto_20170525_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='depositrequest',
            name='transaction_id',
            field=models.CharField(max_length=50, null=True, verbose_name='Transaction id', blank=True),
        ),
    ]
