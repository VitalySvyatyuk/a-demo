# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='language',
            field=models.CharField(default=b'en', max_length=10, verbose_name='Language', db_index=True, choices=[(b'ru', b'Russian'), (b'en', b'English')]),
        ),
    ]
