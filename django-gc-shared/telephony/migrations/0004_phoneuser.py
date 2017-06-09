# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telephony', '0003_auto_20160202_1902'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneUser',
            fields=[
                ('login', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('password', models.CharField(max_length=250)),
                ('nat', models.CharField(default=b'0', help_text=b"Enables Asterisk NAT mode; try changing if connection doesn't work", max_length=1, choices=[(b'0', b'No'), (b'1', b'Yes')])),
                ('permit', models.CharField(default=b'', help_text=b'CIDR notation, e.g. 192.168.0.1/24&10.1.0.1/24', max_length=10000, verbose_name=b'Allowed IPs', blank=True)),
                ('deny', models.CharField(default=b'', help_text=b'CIDR notation, e.g. 192.168.0.1/24&10.1.0.1/24', max_length=10000, verbose_name=b'Denied IPs', blank=True)),
                ('enabled', models.CharField(default=b'1', max_length=1, choices=[(b'0', b'No'), (b'1', b'Yes')])),
                ('office', models.CharField(default=b'', max_length=3, verbose_name=b'Internal number', blank=True)),
                ('sync', models.CharField(default=b'0', verbose_name=b'Synced with asterisk', max_length=1, editable=False, choices=[(b'0', b'No'), (b'1', b'Yes')])),
                ('queue', models.CharField(default=b'null', max_length=50, choices=[(b'en', b'English queue'), (b'ru', b'Russian queue'), (b'null', b'No queue')])),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]
