# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uptrader_cms', '0006_auto_20170118_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='legaldocument',
            name='category',
            field=models.CharField(max_length=100, verbose_name='Category', choices=[(b'docs', 'Documents'), (b'policy', 'Privacy Policy'), (b'risks', 'Risk Disclosure'), (b'regulation', 'Regulation'), (b'cookies', 'Cookie Policy'), (b'agents', 'Agents and Representatives')]),
        ),
    ]
