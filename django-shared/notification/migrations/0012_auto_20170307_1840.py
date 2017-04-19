# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0011_auto_20170221_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='language',
            field=models.CharField(default=b'ru', max_length=10, verbose_name=b'Language', choices=[(b'ru', b'Russian'), (b'en', b'English')]),
        ),
        migrations.AlterField(
            model_name='notificationsettings',
            name='language',
            field=models.CharField(default=b'ru', unique=True, max_length=10, verbose_name=b'Language', choices=[(b'ru', b'Russian'), (b'en', b'English')]),
        ),
    ]
