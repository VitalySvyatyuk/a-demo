# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telephony', '0004_phoneuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calldetailrecord',
            name='call_date',
            field=models.DateTimeField(verbose_name="Call's date"),
        ),
        migrations.AlterField(
            model_name='calldetailrecord',
            name='external_cdr_id',
            field=models.IntegerField(unique=True, verbose_name='External ID'),
        ),
        migrations.AlterField(
            model_name='calldetailrecord',
            name='name_a',
            field=models.CharField(max_length=64, null=True, verbose_name='A-User Asterisk', blank=True),
        ),
        migrations.AlterField(
            model_name='calldetailrecord',
            name='name_b',
            field=models.CharField(max_length=64, null=True, verbose_name='B-User Asterisk', blank=True),
        ),
        migrations.AlterField(
            model_name='calldetailrecord',
            name='number_a',
            field=models.CharField(max_length=64, null=True, verbose_name='A-Number Asterisk', blank=True),
        ),
        migrations.AlterField(
            model_name='calldetailrecord',
            name='number_b',
            field=models.CharField(max_length=64, null=True, verbose_name='B-Number Asterisk', blank=True),
        ),
        migrations.AlterField(
            model_name='calldetailrecord',
            name='price',
            field=models.DecimalField(null=True, verbose_name='Price', max_digits=6, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='calldetailrecord',
            name='recording_file',
            field=models.CharField(max_length=255, null=True, verbose_name='Record', blank=True),
        ),
    ]
