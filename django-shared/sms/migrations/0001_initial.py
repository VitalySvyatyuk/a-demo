# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SMSMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('backend', models.CharField(max_length=100, editable=False)),
                ('code', models.CharField(max_length=100, editable=False)),
                ('receiver_number', models.CharField(help_text='A number in format +70000000000', max_length=50, verbose_name='Receiver number')),
                ('sender_number', models.CharField(editable=False, max_length=50, blank=True, help_text="Leave empty if you don't know what it is", null=True, verbose_name='Sender number')),
                ('text', models.TextField(help_text='Maximum 160 characters', verbose_name='Message text')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('params', django.contrib.postgres.fields.hstore.HStoreField(default={})),
            ],
            options={
                'verbose_name': 'SMS message',
                'verbose_name_plural': 'SMS messages',
            },
        ),
    ]
