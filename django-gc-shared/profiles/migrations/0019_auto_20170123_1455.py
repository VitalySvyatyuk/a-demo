# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0018_auto_20170123_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='nature_of_biz',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='Nature of business', choices=[(b'Accountancy', 'Accountancy'), (b'Admin/secretarial', 'Admin/ secretarial'), (b'Agricultural', 'Agricultural'), (b'Art', 'Art'), (b'Financial/Banking', 'Financial/Banking'), (b'Catering/Hospitality', 'Catering/Hospitality'), (b'Creative/Media', 'Creative/Media'), (b'Educational', 'Educational'), (b'Emergency', 'Emergency'), (b'Engineering', 'Engineering'), (b'Health/Medicine', 'Health/Medicine'), (b'IT', 'IT'), (b'Legal', 'Legal'), (b'Leisure/ Entertainment/ Tourism', 'Leisure/ Entertainment/ Tourism'), (b'Manufacturing', 'Manufacturing'), (b'Marketing/ Advertising/ PR', 'Marketing/ Advertising/ PR'), (b'Property', 'Property'), (b'Sales', 'Sales'), (b'Social', 'Social'), (b'Telecom', 'Telecom'), (b'Transport/ Logistics', 'Transport/ Logistics'), (b'Other', 'Other')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='purpose',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Purpose to open an Arum capital account', choices=[(b'Investment', 'Investment'), (b'Hedging', 'Hedging'), (b'Speculative trading', 'Speculative trading')]),
        ),
    ]
