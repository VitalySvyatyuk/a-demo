# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('callback_request', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callbackrequest',
            name='category',
            field=models.CharField(default=b'general', max_length=255, choices=[(b'general', 'General questions'), (b'financial', 'Financial questions'), (b'technical', 'Technical questions')]),
        ),
    ]
