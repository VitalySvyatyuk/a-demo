# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0036_userprofile_is_partner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='account_turnover',
            field=models.IntegerField(null=True, verbose_name='Approximate volume of investments per annum (USD)', blank=True),
        ),
    ]
