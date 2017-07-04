# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0038_auto_20170630_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='city',
            field=models.CharField(help_text='The city where you live', max_length=100, null=True, verbose_name='City', blank=True),
        ),
    ]
