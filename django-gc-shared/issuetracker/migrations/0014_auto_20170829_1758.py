# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issuetracker', '0013_auto_20170728_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='internaltransferissue',
            name='currency',
            field=models.CharField(default=b'USD', choices=[(b'RUR', b'RUR'), (b'USD', b'USD')], max_length=6, blank=True, null=True, verbose_name='Currency'),
        ),
    ]
