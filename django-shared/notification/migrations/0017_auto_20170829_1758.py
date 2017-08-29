# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0016_auto_20170728_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='language',
            field=models.CharField(default=b'en', max_length=10, verbose_name=b'Language', choices=[(b'ru', b'Russian'), (b'en', b'English')]),
        ),
        migrations.AlterField(
            model_name='notificationsettings',
            name='language',
            field=models.CharField(default=b'en', unique=True, max_length=10, verbose_name=b'Language', choices=[(b'ru', b'Russian'), (b'en', b'English')]),
        ),
    ]
