# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0002_auto_20170221_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='language',
            field=models.CharField(default=b'ru', max_length=10, verbose_name='Language', db_index=True, choices=[(b'ru', b'Russian'), (b'en', b'English')]),
        ),
    ]
