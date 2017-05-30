# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0002_auto_20170524_0044'),
        ('private_messages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='campaign',
            field=models.ForeignKey(blank=True, to='massmail.Campaign', null=True),
        ),
    ]
