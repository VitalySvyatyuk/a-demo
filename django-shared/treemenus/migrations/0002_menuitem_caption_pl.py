# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treemenus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='caption_pl',
            field=models.CharField(max_length=150, null=True, verbose_name='Caption Polish', blank=True),
        ),
    ]
