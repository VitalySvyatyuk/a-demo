# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0013_auto_20170118_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='purpose',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Your purpose to open an Arum capital account', choices=[(b'Investment', 'Investment'), (b'Hedging', 'Hedging'), (b'Speculative trading', 'Speculative trading')]),
        ),
    ]
