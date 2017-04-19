# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uptrader_cms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='companynews',
            name='image',
            field=models.ImageField(max_length=2048, null=True, upload_to=b'news_images/%Y/%m/%d', blank=True),
        ),
    ]
