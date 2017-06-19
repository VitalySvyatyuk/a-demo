# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0029_auto_20170215_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdocument',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Document name', choices=[(b'passport_scan', 'Proof of Identification'), (b'residential_address', 'Copy of your passport page with the registered residential address'), (b'address_proof', 'Proof of residential address'), (b'driver_license', 'Driver license'), (b'Credit_card_back_side', 'Credit card back side'), (b'Credit_card_front_side', 'Credit card front side'), (b'real_ib_agreement', 'Real IB agreement'), (b'other', 'Other document')]),
        ),
    ]
