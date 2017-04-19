# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0022_auto_20170127_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='tax_residence',
            field=models.ForeignKey(related_name='taxes', verbose_name='Tax residence', blank=True, to='geobase.Country', null=True),
        ),
    ]
