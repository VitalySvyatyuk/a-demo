# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otpdevice',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Is deleted?'),
        ),
        migrations.AlterField(
            model_name='smsdevice',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Is deleted?'),
        ),
        migrations.AlterField(
            model_name='voicedevice',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Is deleted?'),
        ),
    ]
