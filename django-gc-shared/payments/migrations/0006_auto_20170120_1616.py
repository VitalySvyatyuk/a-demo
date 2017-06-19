# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_auto_20161015_1836'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='additionaltransaction',
            options={'verbose_name': 'Manual transaction', 'verbose_name_plural': 'Manual transactions'},
        ),
    ]
