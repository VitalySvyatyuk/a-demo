# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_auto_20161014_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentcategory',
            name='name_en',
            field=models.CharField(max_length=160, null=True, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='paymentcategory',
            name='name_ru',
            field=models.CharField(max_length=160, null=True, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='commission_en',
            field=models.CharField(default='', max_length=150, null=True, verbose_name='Commission', blank=True),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='commission_ru',
            field=models.CharField(default='', max_length=150, null=True, verbose_name='Commission', blank=True),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='link_en',
            field=models.URLField(null=True, verbose_name='Link to payment process'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='link_ru',
            field=models.URLField(null=True, verbose_name='Link to payment process'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='name_en',
            field=models.CharField(max_length=100, null=True, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='name_ru',
            field=models.CharField(max_length=100, null=True, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='processing_times_en',
            field=models.CharField(default='', max_length=150, null=True, verbose_name='Processing times', blank=True),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='processing_times_ru',
            field=models.CharField(default='', max_length=150, null=True, verbose_name='Processing times', blank=True),
        ),
    ]
