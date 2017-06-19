# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import otp.models
from django.conf import settings
import geobase.phone_code_widget


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OTPDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The human-readable name of this device.', max_length=64)),
                ('confirmed', models.BooleanField(default=True, help_text='Is this device ready for use?')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u0423\u0434\u0430\u043b\u0435\u043d?')),
                ('key', models.CharField(default=otp.models.random_base32, help_text='A secret key', max_length=80)),
                ('step', models.PositiveSmallIntegerField(default=30, help_text='The time step in seconds.', blank=True)),
                ('t0', models.BigIntegerField(default=0, help_text='The Unix time at which to begin counting steps.', blank=True)),
                ('digits', models.PositiveSmallIntegerField(default=6, help_text='The number of digits to expect in a token.', blank=True, choices=[(6, 6), (8, 8)])),
                ('tolerance', models.PositiveSmallIntegerField(default=1, help_text='The number of time steps in the past or future to allow.', blank=True)),
                ('drift', models.SmallIntegerField(default=0, help_text='The number of time steps the prover is known to deviate from our clock.', blank=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='Added at')),
                ('user', models.ForeignKey(help_text='The user that this device belongs to.', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'profiles_otpdevice',
                'verbose_name': 'OTP device',
                'verbose_name_plural': 'OTP devices',
            },
        ),
        migrations.CreateModel(
            name='SMSDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The human-readable name of this device.', max_length=64)),
                ('confirmed', models.BooleanField(default=True, help_text='Is this device ready for use?')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u0423\u0434\u0430\u043b\u0435\u043d?')),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='Added at')),
                ('phone_number', geobase.phone_code_widget.CountryPhoneCodeField(max_length=40, null=True, verbose_name=b'Phone')),
                ('user', models.ForeignKey(help_text='The user that this device belongs to.', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'profiles_smsdevice',
                'verbose_name': 'SMS Device',
                'verbose_name_plural': 'SMS Devices',
            },
        ),
        migrations.CreateModel(
            name='VoiceDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The human-readable name of this device.', max_length=64)),
                ('confirmed', models.BooleanField(default=True, help_text='Is this device ready for use?')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u0423\u0434\u0430\u043b\u0435\u043d?')),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='Added at')),
                ('user', models.ForeignKey(help_text='The user that this device belongs to.', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'db_table': 'profiles_voicedevice',
                'verbose_name': 'Voice Device',
                'verbose_name_plural': 'Voice Devices',
            },
        ),
    ]
