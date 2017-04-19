# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0020_auto_20170124_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdocument',
            name='is_rejected',
            field=models.BooleanField(default=False, verbose_name='Documents was rejected'),
        ),
    ]
