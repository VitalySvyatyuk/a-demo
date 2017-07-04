# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0037_auto_20170628_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='city',
            field=models.CharField(default=b'', help_text='The city where you live', max_length=100, verbose_name='City', blank=True),
        ),
    ]
