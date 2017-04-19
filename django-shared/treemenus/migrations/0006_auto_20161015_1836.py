# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treemenus', '0005_auto_20160714_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='icon',
            field=models.CharField(max_length=150, null=True, verbose_name='Icon', blank=True),
        ),
    ]
