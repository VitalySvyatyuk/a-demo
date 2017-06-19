# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treemenus', '0006_auto_20161015_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='target_blank',
            field=models.BooleanField(default=False, help_text='If checked open link in new page', verbose_name='Open in blank page'),
        ),
    ]
