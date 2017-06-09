# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gcrm', '0017_auto_20151218_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='user',
            field=models.OneToOneField(related_name='gcrm_contact', null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
