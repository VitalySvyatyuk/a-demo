# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gcrm', '0011_auto_20151214_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='closed_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
