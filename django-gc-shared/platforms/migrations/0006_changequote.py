# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforms', '0005_delete_mt4openprice'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeQuote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=30, verbose_name='Category name')),
                ('quotes', models.CharField(help_text='Example: EURUSD, GBPUSD, AUDCAD', max_length=1024, verbose_name='List of quotes')),
            ],
            options={
                'verbose_name': 'List of quotes',
            },
        ),
    ]
