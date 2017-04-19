# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('friend_recommend', '0001_initial'),
        ('platforms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recommendation',
            name='ib_account',
            field=models.ForeignKey(blank=True, to='platforms.TradingAccount', null=True),
        ),
        migrations.AddField(
            model_name='recommendation',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
