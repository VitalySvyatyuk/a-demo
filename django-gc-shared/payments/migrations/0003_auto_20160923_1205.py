# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import shared.utils
import payments.models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_auto_20160912_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=160, verbose_name='Name')),
                ('name_ru', models.CharField(max_length=160, null=True, verbose_name='Name')),
                ('name_en', models.CharField(max_length=160, null=True, verbose_name='Name')),
                ('priority', models.PositiveSmallIntegerField(default=0, help_text='defines order in list', verbose_name='Priority')),
            ],
            options={
                'verbose_name': 'Payment category',
                'verbose_name_plural': 'Payment categories',
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payment_type', models.PositiveSmallIntegerField(default=0, verbose_name='Payment type', choices=[(0, 'Deposit'), (1, 'Withdraw')])),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('name_ru', models.CharField(max_length=100, null=True, verbose_name='Name')),
                ('name_en', models.CharField(max_length=100, null=True, verbose_name='Name')),
                ('currency', models.CharField(max_length=100, verbose_name='Currency')),
                ('min_amount', models.DecimalField(null=True, verbose_name='Minimum amount', max_digits=10, decimal_places=2, blank=True)),
                ('max_amount', models.DecimalField(null=True, verbose_name='Maximum amount', max_digits=10, decimal_places=2, blank=True)),
                ('commission', models.CharField(default='', max_length=150, verbose_name='Commission', blank=True)),
                ('commission_ru', models.CharField(default='', max_length=150, null=True, verbose_name='Commission', blank=True)),
                ('commission_en', models.CharField(default='', max_length=150, null=True, verbose_name='Commission', blank=True)),
                ('processing_times', models.CharField(default='', max_length=150, verbose_name='Processing times', blank=True)),
                ('processing_times_ru', models.CharField(default='', max_length=150, null=True, verbose_name='Processing times', blank=True)),
                ('processing_times_en', models.CharField(default='', max_length=150, null=True, verbose_name='Processing times', blank=True)),
                ('image', models.ImageField(help_text='Payment system image', upload_to=shared.utils.UploadTo('payments/logos'), null=True, verbose_name='Image', blank=True)),
                ('link', models.URLField(verbose_name='Link to payment process')),
                ('link_ru', models.URLField(null=True, verbose_name='Link to payment process')),
                ('link_en', models.URLField(null=True, verbose_name='Link to payment process')),
                ('languages', django.contrib.postgres.fields.ArrayField(default=payments.models.ps_default_languages, base_field=models.CharField(max_length=10), size=None)),
                ('category', models.ForeignKey(verbose_name='Category', to='payments.PaymentCategory')),
            ],
            options={
                'verbose_name': 'Payment method',
                'verbose_name_plural': 'Payment methods',
            },
        ),
    ]
