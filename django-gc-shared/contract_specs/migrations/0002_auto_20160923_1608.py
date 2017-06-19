# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract_specs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstrumentSpecification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instrument', models.CharField(max_length=100, verbose_name='Instrument')),
                ('description', models.TextField(verbose_name='Description')),
                ('description_ru', models.TextField(null=True, verbose_name='Description')),
                ('description_en', models.TextField(null=True, verbose_name='Description')),
                ('currency', models.CharField(max_length=100, verbose_name='Currency')),
                ('min_price_change', models.CharField(max_length=100, verbose_name='Minimum price change')),
                ('min_order_size', models.CharField(max_length=100, verbose_name='Minimum contract size')),
                ('min_order_size_change', models.CharField(max_length=100, verbose_name='Minimum contract size change')),
                ('min_order_pip_value', models.CharField(max_length=100, verbose_name='Pip value per minimum contract')),
                ('swap_long', models.CharField(max_length=100, verbose_name='SWAP Long')),
                ('swap_short', models.CharField(max_length=100, verbose_name='SWAP Short')),
                ('weekday_margin', models.CharField(max_length=100, verbose_name='Weekday pledge')),
                ('weekend_margin', models.CharField(max_length=100, verbose_name='Weekend pledge')),
            ],
            options={
                'verbose_name': 'Instrument specification',
                'verbose_name_plural': 'Instrument specification',
            },
        ),
        migrations.CreateModel(
            name='InstrumentSpecificationCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Name')),
                ('name_ru', models.CharField(max_length=150, null=True, verbose_name='Name')),
                ('name_en', models.CharField(max_length=150, null=True, verbose_name='Name')),
                ('slug', models.SlugField(help_text='short url name', verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Instrument specification category',
                'verbose_name_plural': 'Instrument specification categories',
            },
        ),
        migrations.AddField(
            model_name='instrumentspecification',
            name='category',
            field=models.ForeignKey(verbose_name='Category', to='contract_specs.InstrumentSpecificationCategory'),
        ),
    ]
