# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geobase', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallbackRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=25, verbose_name='Phone')),
                ('email', models.CharField(default=b'', max_length=50, verbose_name='Email', blank=True)),
                ('name', models.CharField(default=b'', max_length=255, verbose_name='Name')),
                ('call_date', models.DateField(auto_now_add=True, verbose_name='Date')),
                ('category', models.CharField(default=b'general', max_length=255, choices=[(b'forgot_password', 'Forgot password'), (b'button_not_working', 'Button not working'), (b'general', 'General'), (b'withdraw', 'A problem with withdrawal'), (b'other', 'Other')])),
                ('comment', models.CharField(default=b'', max_length=255, blank=True)),
                ('time_start', models.CharField(max_length=5, verbose_name='From', blank=True)),
                ('time_end', models.CharField(max_length=5, verbose_name='To', blank=True)),
                ('request_processed', models.BooleanField(default=False, verbose_name='Request processed')),
                ('internal_comment', models.TextField(default=b'', verbose_name='Internal comment', blank=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('country', models.ForeignKey(blank=True, to='geobase.Country', help_text='Example: Russia', null=True, verbose_name='Country')),
            ],
        ),
    ]
