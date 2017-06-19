# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geobase', '0001_initial'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='annual_income',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Annual income (EUR)', choices=[(b'100k', 'over 100 000'), (b'50k', b'50 000 - 100 000'), (b'10k', b'10 000 - 50 000'), (b'0', 'below 10 000')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='derivatives_exp',
            field=models.BooleanField(default=False, verbose_name='Derivatives experience'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='financial_exp',
            field=models.BooleanField(default=False, verbose_name='Financial experience'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='first_name_ru',
            field=models.CharField(default=b'', max_length=45, verbose_name='First name in Russian', blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='forex_exp',
            field=models.BooleanField(default=False, verbose_name='Forex experience'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_name_ru',
            field=models.CharField(default=b'', max_length=45, verbose_name='Last name in Russian', blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='middle_name_ru',
            field=models.CharField(default=b'', max_length=45, verbose_name='Middle name in Russian', blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='nationality',
            field=models.ForeignKey(related_name='nations', blank=True, to='geobase.Country', help_text='Example: Russia', null=True, verbose_name='Nationality'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='net_capital',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Net capital (EUR)', choices=[(b'100k', 'over 100 000'), (b'50k', b'50 000 - 100 000'), (b'10k', b'10 000 - 50 000'), (b'0', 'below 10 000')]),
        ),
        migrations.AlterField(
            model_name='userdocument',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Document name', choices=[(b'passport_scan', 'Copy of the first page of your passport'), (b'residential_address', 'Copy of your passport page with the registered residential address'), (b'address_proof', 'Proof of residential address'), (b'driver_license', 'Driver license'), (b'birth_certificate', 'Certificate of birth'), (b'real_ib_agreement', 'Real IB agreement'), (b'other', 'Other document')]),
        ),
    ]
