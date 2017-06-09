# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treemenus', '0002_menuitem_caption_pl'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='caption_pt',
            field=models.CharField(max_length=150, null=True, verbose_name='Caption Portuguese', blank=True),
        ),
    ]
