# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0002_auto_20170524_0044'),
        ('profiles', '0034_auto_20170529_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='subscription',
            field=models.ManyToManyField(to='massmail.CampaignType', null=True, verbose_name='\u0422\u0438\u043f \u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0438', blank=True),
        ),
    ]
