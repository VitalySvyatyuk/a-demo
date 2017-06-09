# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0003_auto_20151130_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='manager',
            field=models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='user',
            field=models.ForeignKey(related_name='gcrm_contact', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
