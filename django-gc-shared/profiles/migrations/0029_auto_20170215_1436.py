# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0028_auto_20170213_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='education_level',
            field=models.CharField(max_length=90, null=True, verbose_name='Level of education', blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='nature_of_biz',
            field=models.CharField(max_length=90, null=True, verbose_name='Nature of business', blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='source_of_funds',
            field=models.CharField(max_length=90, null=True, verbose_name='Source of funds', blank=True),
        ),
    ]
