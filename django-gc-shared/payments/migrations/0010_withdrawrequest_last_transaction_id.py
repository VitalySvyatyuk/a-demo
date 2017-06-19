# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0009_depositrequest_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawrequest',
            name='last_transaction_id',
            field=models.CharField(max_length=127, null=True, verbose_name='Last transaction id on this account', blank=True),
        ),
    ]
