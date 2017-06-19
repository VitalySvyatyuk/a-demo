# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforms', '0004_mt4openprice'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Mt4OpenPrice',
        ),
    ]
