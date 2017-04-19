# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referral', '0002_auto_20161014_1802'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='partnercertificateissue',
            options={'verbose_name': 'Application for certificate creation', 'verbose_name_plural': 'Applications for certificate creation'},
        ),
    ]
