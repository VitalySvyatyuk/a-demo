# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0021_userdocument_is_rejected'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='allow_open_invest',
            field=models.BooleanField(default=False, verbose_name='Can open ECN.Invest accounts'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='risk_appetite',
            field=models.BooleanField(default=False, verbose_name='Forex and CFDs are acceptable for my risk appetite'),
        ),
    ]
