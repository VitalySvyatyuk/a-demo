# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0027_userprofile_education_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdocument',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Document name', choices=[(b'passport_scan', 'Proof of Identification'), (b'residential_address', 'Copy of your passport page with the registered residential address'), (b'address_proof', 'Proof of residential address'), (b'driver_license', 'Driver license'), (b'birth_certificate', 'Certificate of birth'), (b'real_ib_agreement', 'Real IB agreement'), (b'other', 'Other document')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='derivative_instruments',
            field=django_hstore.fields.DictionaryField(default={b'Derivative instruments (incl. options, futures, swaps, FRAs, etc.)': b'No'}),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='forex_instruments',
            field=django_hstore.fields.DictionaryField(default={b'Trading experience FOREX/CFDs': b'No'}),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='investment_undertaking',
            field=django_hstore.fields.DictionaryField(default={b'Units of collective investment undertaking': b'No'}),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='transferable_securities',
            field=django_hstore.fields.DictionaryField(default={b'Transferable securities': b'No'}),
        ),
    ]
