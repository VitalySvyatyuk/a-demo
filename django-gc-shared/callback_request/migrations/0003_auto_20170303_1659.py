# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('callback_request', '0002_auto_20161213_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callbackrequest',
            name='category',
            field=models.CharField(default=b'partnership', max_length=255, choices=[(b'general', 'General questions'), (b'financial', 'Financial questions'), (b'technical', 'Technical questions'), (b'partnership', 'Request for partnership')]),
        ),
    ]
