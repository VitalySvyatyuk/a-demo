# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issuetracker', '0001_initial'),
        ('profiles', '0001_initial'),
        ('platforms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='restorefromarchiveissue',
            name='account',
            field=models.ForeignKey(verbose_name='account', to='platforms.TradingAccount'),
        ),
        migrations.AddField(
            model_name='internaltransferissue',
            name='sender',
            field=models.ForeignKey(related_name='transfers', verbose_name='sender', to='platforms.TradingAccount'),
        ),
        migrations.AddField(
            model_name='checkdocumentissue',
            name='document',
            field=models.ForeignKey(verbose_name='document', to='profiles.UserDocument'),
        ),
    ]
