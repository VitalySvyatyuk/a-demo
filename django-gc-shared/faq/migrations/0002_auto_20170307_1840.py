# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faq', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='faq_version',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u0412\u0435\u0440\u0441\u0438\u044f FAQ', choices=[(0, b'Main FAQ'), (1, b'Glossary'), (2, b'Instruments information')]),
        ),
    ]
