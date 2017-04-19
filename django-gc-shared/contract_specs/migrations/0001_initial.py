# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('external', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstrumentsByGroup',
            fields=[
                ('account_group', models.CharField(max_length=32, db_column=b'MT_GROUP')),
                ('symbol_group', models.CharField(max_length=32, serialize=False, primary_key=True, db_column=b'SYMBOL_GROUP')),
                ('changed_at', models.DateTimeField(db_column=b'MODIFY_TIME')),
            ],
            options={
                'db_table': 'mt4_securities',
            },
        ),
        migrations.CreateModel(
            name='SymbolDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('symbol', models.CharField(max_length=25, verbose_name=b'Symbol')),
                ('type', models.CharField(default=b'symbol', max_length=100, verbose_name=b'Object Type', choices=[(b'instrument', b'Instrument'), (b'symbol', b'Symbol')])),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('description_ru', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('description_en', models.TextField(null=True, verbose_name=b'Description', blank=True)),
            ],
            options={
                'verbose_name': 'Symbol description',
            },
        ),
        migrations.CreateModel(
            name='SymbolsByInstrument',
            fields=[
                ('symbol', models.CharField(max_length=100, serialize=False, primary_key=True, db_column=b'symbol_name')),
                ('instrument', models.CharField(max_length=100, null=True, db_column=b'instrument_name')),
                ('update_ts', models.DateTimeField(auto_now=True, db_column=b'MODIFY_TIME')),
            ],
            options={
                'db_table': 'mt4_instruments',
            },
        ),
        migrations.CreateModel(
            name='Instruments',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('external.mt4instruments',),
        ),
    ]
