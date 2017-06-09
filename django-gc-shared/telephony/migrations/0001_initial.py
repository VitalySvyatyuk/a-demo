# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalAsteriskCDR',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, db_column=b'cdr_id')),
                ('calldate', models.DateTimeField(auto_now_add=True)),
                ('clid', models.CharField(default='', max_length=80)),
                ('src', models.CharField(default='', max_length=80)),
                ('dst', models.CharField(default='', max_length=80)),
                ('dcontext', models.CharField(default='', max_length=80)),
                ('channel', models.CharField(default='', max_length=80)),
                ('dstchannel', models.CharField(default='', max_length=80)),
                ('lastapp', models.CharField(default='', max_length=80)),
                ('lastdata', models.CharField(default='', max_length=80)),
                ('duration', models.IntegerField(default=0)),
                ('billsec', models.IntegerField(default=0)),
                ('disposition', models.CharField(default='', max_length=45)),
                ('amaflags', models.IntegerField(default=0)),
                ('accountcode', models.CharField(default='', max_length=20)),
                ('uniqueid', models.CharField(default='', max_length=32)),
                ('recordingfile', models.CharField(default='', max_length=255)),
                ('userfield', models.CharField(default='', max_length=255)),
            ],
            options={
                'db_table': 'cdr',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CallDetailRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('external_cdr_id', models.IntegerField(unique=True, verbose_name='\u0412\u043d\u0435\u0448\u043d\u0438\u0439 ID')),
                ('name_a', models.CharField(max_length=64, null=True, verbose_name='A-\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c Asterisk', blank=True)),
                ('name_b', models.CharField(max_length=64, null=True, verbose_name='B-\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c Asterisk', blank=True)),
                ('number_a', models.CharField(max_length=64, null=True, verbose_name='A-\u041d\u043e\u043c\u0435\u0440 Asterisk', blank=True)),
                ('number_b', models.CharField(max_length=64, null=True, verbose_name='B-\u041d\u043e\u043c\u0435\u0440 Asterisk', blank=True)),
                ('duration', models.IntegerField(default=0, null=True, blank=True)),
                ('disposition', models.CharField(default='', max_length=64, null=True, blank=True)),
                ('recording_file', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u043f\u0438\u0441\u044c', blank=True)),
                ('call_date', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0432\u043e\u043d\u043a\u0430')),
                ('price', models.DecimalField(null=True, verbose_name='\u0426\u0435\u043d\u0430', max_digits=6, decimal_places=2, blank=True)),
                ('user_a', models.ForeignKey(related_name='outbound_calls', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user_b', models.ForeignKey(related_name='inbound_calls', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VoiceMailCDR',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_manual', models.BooleanField(default=False, help_text='\u0422\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044f \u0440\u0443\u0447\u043d\u0430\u044f \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u0447\u0435\u0440\u0435\u0437 \u041e\u041a\u041f, \u0442\u0430\u043a \u043a\u0430\u043a \u043d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0438\u0442\u044c \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0430 \u0434\u0430\u043d\u043d\u043e\u0433\u043e \u043a\u043b\u0438\u0435\u043d\u0442\u0430', verbose_name='\u0420\u0443\u0447\u043d\u0430\u044f \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430')),
                ('comment', models.TextField(help_text='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439 \u043e \u0437\u0432\u043e\u043d\u043a\u0435, \u0435\u0441\u043b\u0438 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e', null=True, blank=True)),
                ('call_date', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0432\u043e\u043d\u043a\u0430')),
                ('cdr', models.OneToOneField(related_name='voicemail', to='telephony.CallDetailRecord')),
                ('last_commented_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
