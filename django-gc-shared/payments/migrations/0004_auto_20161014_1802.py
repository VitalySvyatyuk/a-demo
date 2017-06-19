# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_auto_20160923_1205'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='additionaltransaction',
            name='trade_id',
        ),
        migrations.RemoveField(
            model_name='baserequest',
            name='trade_id',
        ),
        migrations.RemoveField(
            model_name='paymentcategory',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='paymentcategory',
            name='name_ru',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='commission_en',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='commission_ru',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='link_en',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='link_ru',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='name_ru',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='processing_times_en',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='processing_times_ru',
        ),
    ]
