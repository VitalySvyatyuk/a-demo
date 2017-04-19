# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issuetracker', '0005_approveopenecnissue'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='approveopenecnissue',
            options={'verbose_name': 'Approve open ECN.Invest account', 'verbose_name_plural': 'Approves open ECN.Invest account'},
        ),
        migrations.AddField(
            model_name='approveopenecnissue',
            name='allow_open_invest',
            field=models.BooleanField(default=False, verbose_name='Can open ECN.Invest accounts'),
        ),
    ]
