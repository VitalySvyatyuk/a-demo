# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issuetracker', '0009_auto_20170307_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genericissue',
            name='internal_description',
            field=models.TextField(help_text=b'Client does not see that field', verbose_name='Internal description', blank=True),
        ),
    ]
