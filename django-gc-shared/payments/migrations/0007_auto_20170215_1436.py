# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_auto_20170120_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionaltransaction',
            name='currency',
            field=models.CharField(max_length=6, null=True, verbose_name='Currency', choices=[(b'USD', b'USD')]),
        ),
        migrations.AlterField(
            model_name='baserequest',
            name='currency',
            field=models.CharField(max_length=6, verbose_name='Currency', choices=[(b'USD', b'USD')]),
        ),
    ]
