# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0013_subscribed_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopupCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('appeared', models.PositiveIntegerField(default=0, verbose_name=b'Appeared')),
                ('subscribed', models.PositiveIntegerField(default=0, verbose_name=b'Subscribed')),
            ],
        ),
    ]
