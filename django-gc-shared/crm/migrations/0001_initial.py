# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import time

import django.db.models.deletion
import jsonfield.fields
from django.conf import settings
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('platforms', '0003_auto_20161014_1802'),
        ('geobase', '0001_initial'),
        ('node', '0001_initial'),
    ]

    operations = [

        migrations.CreateModel(
            name='RegionalOffice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True,
                                                  verbose_name='\u041e\u0444\u0438\u0441 \u0430\u043a\u0442\u0438\u0432\u0435\u043d')),
                ('slug', models.SlugField(
                    help_text='\u041c\u0430\u0448\u0438\u043d\u043d\u043e\u0435 \u0438\u043c\u044f, \u0434\u043b\u044f \u0441\u0441\u044b\u043b\u043e\u043a',
                    verbose_name='\u0421\u043b\u0430\u0433')),
                ('name', models.CharField(max_length=50, verbose_name='\u0413\u043e\u0440\u043e\u0434')),
                ('name_ru', models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434')),
                ('name_en', models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434')),
                ('name_zh_cn',
                 models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434')),
                ('name_id', models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434')),
                ('caption', models.CharField(max_length=150, null=True,
                                             verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a',
                                             blank=True)),
                ('caption_ru', models.CharField(max_length=150, null=True,
                                                verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a',
                                                blank=True)),
                ('caption_en', models.CharField(max_length=150, null=True,
                                                verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a',
                                                blank=True)),
                ('caption_zh_cn', models.CharField(max_length=150, null=True,
                                                   verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a',
                                                   blank=True)),
                ('caption_id', models.CharField(max_length=150, null=True,
                                                verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a',
                                                blank=True)),
                ('description',
                 models.TextField(null=True, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435',
                                  blank=True)),
                ('address', models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441')),
                ('address_ru', models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441')),
                ('address_en', models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441')),
                ('address_zh_cn', models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441')),
                ('address_id', models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441')),
                ('metro', models.CharField(
                    help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                    max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True)),
                ('metro_ru', models.CharField(
                    help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                    max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True)),
                ('metro_en', models.CharField(
                    help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                    max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True)),
                ('metro_zh_cn', models.CharField(
                    help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                    max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True)),
                ('metro_id', models.CharField(
                    help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                    max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True)),
                ('email', models.EmailField(max_length=75, null=True,
                                            verbose_name='E-mail \u043e\u0444\u0438\u0441\u0430 (\u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0439)',
                                            blank=True)),
                ('phone', models.CharField(max_length=20, null=True,
                                           verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d\u0430 \u043e\u0444\u0438\u0441\u0430',
                                           blank=True)),
                ('agent_codes', models.CommaSeparatedIntegerField(
                    help_text='\u0427\u0435\u0440\u0435\u0437 \u0437\u0430\u043f\u044f\u0442\u0443\u044e, \u0431\u0435\u0437 \u043f\u0440\u043e\u0431\u0435\u043b\u043e\u0432',
                    max_length=1024, null=True,
                    verbose_name='\u041f\u0430\u0440\u0442\u043d\u0435\u0440\u0441\u043a\u0438\u0435 \u043d\u043e\u043c\u0435\u0440\u0430',
                    blank=True)),
                ('can_deposit_or_withdraw', models.BooleanField(default=False,
                                                                verbose_name='\u041c\u043e\u0436\u0435\u0442 \u0441\u043e\u0432\u0435\u0440\u0448\u0430\u0442\u044c \u0432\u0432\u043e\u0434/\u0432\u044b\u0432\u043e\u0434 \u043d\u0430\u043b\u0438\u0447\u043d\u044b\u043c\u0438')),
                ('emails', models.CharField(default=b'partner@grandcapital.net',
                                            help_text='\u0447\u0435\u0440\u0435\u0437 \u0437\u0430\u043f\u044f\u0442\u0443\u044e',
                                            max_length=255,
                                            verbose_name="Email'\u044b, \u043d\u0430 \u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u0441\u043b\u0430\u0442\u044c \u0437\u0430\u043f\u0440\u043e\u0441\u044b \u043d\u0430 \u043e\u0431\u0443\u0447\u0435\u043d\u0438\u0435")),
                ('hidden', models.BooleanField(default=False,
                                               help_text='\u0415\u0441\u043b\u0438 \u043e\u0442\u043c\u0435\u0447\u0435\u043d\u043e, \u043e\u0444\u0438\u0441 \u0431\u0443\u0434\u0435\u0442 \u0442\u043e\u043b\u044c\u043a\u043e \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c\u0441\u044f \u0432 \u0441\u043f\u0438\u0441\u043a\u0435',
                                               verbose_name='\u0422\u043e\u043b\u044c\u043a\u043e \u043a\u043e\u043d\u0442\u0430\u043a\u0442\u044b')),
                ('is_our', models.BooleanField(default=False,
                                               help_text='\u0415\u0441\u043b\u0438 \u043d\u0435 \u043e\u0442\u043c\u0435\u0447\u0435\u043d\u043e, \u043a\u043b\u0438\u0435\u043d\u0442\u044b \u043e\u0444\u0438\u0441\u0430 \u043d\u0435 \u0431\u0443\u0434\u0443\u0442 \u043a\u0440\u0435\u043f\u0438\u0442\u044c\u0441\u044f \u043a \u043d\u0430\u0448\u0438\u043c \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0430\u043c',
                                               verbose_name='\u041d\u0430\u0448 \u0444\u0438\u043b\u0438\u0430\u043b')),
                ('yd_map_x', models.FloatField(null=True,
                                               verbose_name='X \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u0430 YandexMaps',
                                               blank=True)),
                ('yd_map_y', models.FloatField(null=True,
                                               verbose_name='Y \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u0430 YandexMaps',
                                               blank=True)),
                ('country', models.ForeignKey(related_name=b'regional_offices',
                                              verbose_name='\u0421\u0442\u0440\u0430\u043d\u0430',
                                              to='geobase.Country')),
                ('state', models.ForeignKey(related_name=b'regional_offices',
                                            verbose_name='\u0428\u0442\u0430\u0442/\u0420\u0435\u0433\u0438\u043e\u043d',
                                            blank=True, to='geobase.Region', null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': '\u0420\u0435\u0433\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u043e\u0444\u0438\u0441',
                'verbose_name_plural': '\u0420\u0435\u0433\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0435 \u043e\u0444\u0438\u0441\u044b',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AccountDataView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AmoContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('oid', models.BigIntegerField(null=True, verbose_name='\u0418\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440 \u0432 AmoCRM')),
                ('unsynced', models.BooleanField(default=True, verbose_name='\u041d\u0443\u0436\u0434\u0430\u0435\u0442\u0441\u044f \u0432 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438')),
                ('deleted', models.BooleanField(default=False, verbose_name='\u0423\u0434\u0430\u043b\u0451\u043d')),
                ('synced_at', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0439 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438')),
                ('user', models.OneToOneField(related_name='amo', null=True, on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u0441\u0430\u0439\u0442\u0430', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AmoNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('oid', models.BigIntegerField(null=True, verbose_name='\u0418\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440 \u0432 AmoCRM')),
                ('unsynced', models.BooleanField(default=True, verbose_name='\u041d\u0443\u0436\u0434\u0430\u0435\u0442\u0441\u044f \u0432 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438')),
                ('deleted', models.BooleanField(default=False, verbose_name='\u0423\u0434\u0430\u043b\u0451\u043d')),
                ('synced_at', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0439 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438')),
                ('text', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('contact', models.ForeignKey(related_name='notes', verbose_name='\u041a\u043e\u043d\u0442\u0430\u043a\u0442 AmoCRM', to='crm.AmoContact')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AmoTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('oid', models.BigIntegerField(null=True, verbose_name='\u0418\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440 \u0432 AmoCRM')),
                ('unsynced', models.BooleanField(default=True, verbose_name='\u041d\u0443\u0436\u0434\u0430\u0435\u0442\u0441\u044f \u0432 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438')),
                ('deleted', models.BooleanField(default=False, verbose_name='\u0423\u0434\u0430\u043b\u0451\u043d')),
                ('synced_at', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0439 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438')),
                ('type', models.CharField(default=b'CALL', max_length=255, verbose_name='\u0422\u0438\u043f', choices=[(b'CALL', '\u0417\u0432\u043e\u043d\u043e\u043a'), (b'LETTER', '\u041f\u0438\u0441\u044c\u043c\u043e'), (b'MEETING', '\u0412\u0441\u0442\u0440\u0435\u0447\u0430'), (b'3250', '\u041f\u0435\u0440\u0432\u0430\u044f \u0441\u0432\u044f\u0437\u044c')])),
                ('text', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('finish', models.DateTimeField(verbose_name='\u0412\u044b\u043f\u043e\u043b\u043d\u0438\u0442\u044c \u0434\u043e')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('last_modified', models.DateTimeField(auto_now_add=True, verbose_name='\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0435 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435')),
                ('is_completed', models.BooleanField(default=False, verbose_name='\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430')),
                ('assignee', models.ForeignKey(related_name='amo_tasks', verbose_name='\u0418\u0441\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c', to=settings.AUTH_USER_MODEL, null=True)),
                ('contact', models.ForeignKey(related_name='tasks', verbose_name='\u041a\u043e\u043d\u0442\u0430\u043a\u0442 AmoCRM', to='crm.AmoContact', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BrocoMt4Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mt4_id', models.IntegerField()),
                ('group', models.CharField(max_length=50)),
                ('creation_ts', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BrocoUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.CharField(unique=True, max_length=200)),
                ('country', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('state', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=500)),
                ('phone', models.CharField(max_length=500)),
                ('has_only_demo', models.BooleanField(default=False)),
                ('manager', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CallInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0432\u043e\u043d\u043a\u0430')),
                ('comment', models.TextField(null=True, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True)),
                ('caller', models.ForeignKey(verbose_name='\u0417\u0432\u043e\u043d\u0438\u0432\u0448\u0438\u0439 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'date',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CRMAccess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_allowed_ips', models.CharField(help_text='\u041f\u0435\u0440\u0435\u0447\u0438\u0441\u043b\u044f\u0442\u044c \u0447\u0435\u0440\u0435\u0437 \u043f\u0440\u043e\u0431\u0435\u043b. \u0415\u0441\u043b\u0438 \u0443\u043a\u0430\u0437\u0430\u0442\u044c \u0437\u0434\u0435\u0441\u044c "*", \u0442\u043e \u0431\u0443\u0434\u0443\u0442 \u0440\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u044b \u043b\u044e\u0431\u044b\u0435 IP. \u041c\u043e\u0436\u043d\u043e \u0443\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043f\u043e\u0434\u0441\u0435\u0442\u0438: 192.168.1.0/25', max_length=1000, verbose_name='\u0420\u0430\u0437\u0440\u0435\u0448\u0451\u043d\u043d\u044b\u0435 IP-\u0430\u0434\u0440\u0435\u0441\u0430')),
                ('active', models.BooleanField(default=False, verbose_name='\u0410\u043a\u0442\u0438\u0432\u0435\u043d')),
                ('reception_access', models.BooleanField(default=False, help_text='\u041f\u043e\u0437\u0432\u043e\u043b\u044f\u0435\u0442 \u0441\u043c\u043e\u0442\u0440\u0435\u0442\u044c \u0442\u043e\u043b\u044c\u043a\u043e \u043a\u043e\u043d\u0442\u0430\u043a\u0442\u044b \u0438 \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u043e\u0433\u043e \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0430', verbose_name='\u0414\u043e\u0441\u0442\u0443\u043f \u0434\u043b\u044f \u0440\u0435\u0446\u0435\u043f\u0448\u0435\u043d\u0430')),
                ('staff_access', models.BooleanField(default=False, verbose_name='\u041f\u043e\u043b\u043d\u044b\u0439 \u0434\u043e\u0441\u0442\u0443\u043f \u043a CRM')),
                ('view_agent_code', models.BooleanField(default=False, help_text='\u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u0442 \u043a\u043e\u043b\u043e\u043d\u043a\u0443 "\u041a\u043e\u0434 \u0430\u0433\u0435\u043d\u0442\u0430"', verbose_name='\u0412\u0438\u0434\u0435\u043d \u043a\u043e\u0434 \u0430\u0433\u0435\u043d\u0442\u0430')),
                ('view_manager', models.BooleanField(default=False, help_text='\u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u0442 \u043a\u043e\u043b\u043e\u043d\u043a\u0443 "\u041f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440"', verbose_name='\u0412\u0438\u0434\u0435\u043d \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440')),
                ('view_partner_domains', models.BooleanField(default=False, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0434\u0430\u043d\u043d\u044b\u0435 \u043f\u043e \u0441\u0430\u0439\u0442\u0430\u043c \u043f\u0430\u0440\u0442\u043d\u0451\u0440\u043e\u0432')),
                ('ib_access', models.BooleanField(default=False, help_text='\u041d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e \u0442\u0430\u043a\u0436\u0435 \u0437\u0430\u0434\u0430\u0442\u044c \u0441\u0447\u0435\u0442\u0430 \u0432 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0435\u043c \u043f\u043e\u043b\u0435', verbose_name='\u0414\u043e\u0441\u0442\u0443\u043f \u043a \u0441\u0432\u043e\u0438\u043c IB \u043d\u043e\u043c\u0435\u0440\u0430\u043c')),
                ('_ib_accounts', models.TextField(help_text='IB-\u0430\u043a\u043a\u0430\u0443\u043d\u0442\u044b, \u043a \u043a\u043b\u0438\u0435\u043d\u0442\u0430\u043c \u043a\u043e\u0442\u043e\u0440\u044b\u0445 \u043d\u0443\u0436\u043d\u043e \u0434\u0430\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f. \u041d\u0430 \u043e\u0434\u043d\u043e\u0439 \u0441\u0442\u0440\u043e\u0447\u043a\u0435, \u0447\u0435\u0440\u0435\u0437 \u0437\u0430\u043f\u044f\u0442\u0443\u044e', verbose_name='IB-\u0430\u043a\u043a\u0430\u0443\u043d\u0442\u044b', blank=True)),
                ('regional_access_demo', models.IntegerField(default=0, help_text='\u041d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e \u0442\u0430\u043a\u0436\u0435 \u0437\u0430\u0434\u0430\u0442\u044c \u0433\u043e\u0440\u043e\u0434\u0430 \u0438 \u043e\u0431\u043b\u0430\u0441\u0442\u0438 \u0432 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0435\u043c \u043f\u043e\u043b\u0435', verbose_name='\u0414\u043e\u0441\u0442\u0443\u043f \u043a \u0440\u0435\u0433\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e\u0439 \u0431\u0430\u0437\u0435 \u0414\u0415\u041c\u041e', choices=[(0, '\u0411\u0435\u0437 \u0434\u043e\u0441\u0442\u0443\u043f\u0430'), (1, '\u0422\u043e\u043b\u044c\u043a\u043e \u043e\u0441\u043d\u043e\u0432\u043d\u0430\u044f \u0431\u0430\u0437\u0430'), (2, '\u0422\u043e\u043b\u044c\u043a\u043e \u0431\u0430\u0437\u0430 Broco'), (3, '\u041f\u043e\u043b\u043d\u044b\u0439 \u0434\u043e\u0441\u0442\u0443\u043f')])),
                ('_cities_and_regions', models.TextField(help_text='\u041d\u0430 \u043e\u0434\u043d\u043e\u0439 \u0441\u0442\u0440\u043e\u0447\u043a\u0435, \u0447\u0435\u0440\u0435\u0437 \u0437\u0430\u043f\u044f\u0442\u0443\u044e', verbose_name='\u0413\u043e\u0440\u043e\u0434\u0430 \u0438 \u043e\u0431\u043b\u0430\u0441\u0442\u0438', blank=True)),
                ('user', models.OneToOneField(related_name='crm_access', verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CRMComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442 \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u044f')),
                ('author', models.ForeignKey(verbose_name='\u0410\u0432\u0442\u043e\u0440', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'creation_ts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomerRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_view_ts', models.DateTimeField(help_text='\u0412\u0440\u0435\u043c\u044f \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0433\u043e \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u0430 \u043f\u043e \u043a\u043d\u043e\u043f\u043a\u0435 "\u041f\u043e\u043b\u0443\u0447\u0438\u0442\u044c \u043a\u043b\u0438\u0435\u043d\u0442\u0430"', null=True, verbose_name='\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440', blank=True)),
                ('broco_user', models.OneToOneField(related_name='crm', null=True, to='crm.BrocoUser')),
                ('grand_user', models.OneToOneField(related_name='crm', null=True, db_column=b'user_id', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FinancialDepartmentCall',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name='\u0418\u043c\u044f \u0437\u0432\u043e\u043d\u0438\u0432\u0448\u0435\u0433\u043e')),
                ('account', models.IntegerField(null=True, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0441\u0447\u0451\u0442\u0430')),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0437\u0432\u043e\u043d\u043a\u0430')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u0437\u0432\u043e\u043d\u043a\u0430')),
                ('callee', models.ForeignKey(verbose_name='\u041f\u0440\u0438\u043d\u044f\u0432\u0448\u0438\u0439 \u0437\u0432\u043e\u043d\u043e\u043a', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('financial_dpt_call', 'Allows access to financial department call form'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LinkRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0430\u044f\u0432\u043a\u0438')),
                ('comment', models.TextField(null=True, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True)),
                ('automatic', models.BooleanField(default=False, verbose_name='\u0410\u0432\u0442\u043e\u043c\u0430\u0442. \u0437\u0430\u044f\u0432\u043a\u0430', editable=False)),
                ('processed', models.BooleanField(default=False, verbose_name='\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u043d\u0430')),
                ('completed', models.BooleanField(default=False, verbose_name='\u0418\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0430')),
                ('account', models.ForeignKey(related_name='link_requests', to='platforms.TradingAccount')),
                ('author', models.ForeignKey(verbose_name='\u0410\u0432\u0442\u043e\u0440 \u0437\u0430\u044f\u0432\u043a\u0438', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(related_name='link_requests', to='crm.CustomerRelationship')),
            ],
            options={
                'get_latest_by': 'date',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ManagerReassignRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(null=True, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True)),
                ('reject_reason', models.TextField(null=True, verbose_name='\u041f\u0440\u0438\u0447\u0438\u043d\u0430 \u043e\u0442\u043a\u0430\u0437\u0430', blank=True)),
                ('status', models.CharField(default=b'new', max_length=255, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', choices=[(b'new', '\u041d\u043e\u0432\u0430\u044f'), (b'accepted', '\u041e\u0434\u043e\u0431\u0440\u0435\u043d\u0430'), (b'rejected', '\u041e\u0442\u043a\u043b\u043e\u043d\u0435\u043d\u0430')])),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0435 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435')),
                ('assign_to', models.ForeignKey(related_name='+', verbose_name='\u0417\u0430\u043a\u0440\u0435\u043f\u0438\u0442\u044c \u0437\u0430', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('author', models.ForeignKey(related_name='+', verbose_name='\u0410\u0432\u0442\u043e\u0440 \u0437\u0430\u044f\u0432\u043a\u0438', to=settings.AUTH_USER_MODEL)),
                ('completed_by', models.ForeignKey(related_name='+', verbose_name='\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u043d\u0430', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('previous', models.ForeignKey(related_name='+', verbose_name='\u041f\u0440\u0435\u0434\u044b\u0434\u0443\u0449\u0438\u0439 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='+', verbose_name='\u041a\u043b\u0438\u0435\u043d\u0442', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'created_at',
                'verbose_name': '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0441\u043c\u0435\u043d\u0443 \u043c\u0435\u043d\u0435\u0436\u0435\u0440\u0430',
                'verbose_name_plural': '\u0417\u0430\u044f\u0432\u043a\u0438 \u043d\u0430 \u0441\u043c\u0435\u043d\u0443 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0430',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'message', max_length=255, verbose_name='\u0422\u0438\u043f', choices=[(b'client_call', '\u0417\u0432\u043e\u043d\u043e\u043a \u043a\u043b\u0438\u0435\u043d\u0442\u0430'), (b'new_client', '\u041d\u043e\u0432\u044b\u0439 \u043a\u043b\u0438\u0435\u043d\u0442'), (b'message', '\u0421\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435')])),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f', null=True)),
                ('sent_at', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043e\u0442\u043f\u0440\u0430\u0432\u043a\u0438')),
                ('is_sent', models.BooleanField(default=False, verbose_name='\u041e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0430')),
                ('text', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('params', jsonfield.fields.JSONField(default={}, verbose_name='\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0435 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b')),
                ('user', models.ForeignKey(related_name='+', verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonalManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_office_supermanager', models.BooleanField(default=False, help_text='\u0421\u0443\u043f\u0435\u0440-\u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0441\u0432\u043e\u0435\u0433\u043e \u043e\u0444\u0438\u0441\u0430, \u0438\u043c\u0435\u0435\u0442 \u043f\u0440\u0430\u0432\u043e \u0443\u043f\u0440\u0430\u0432\u043b\u044f\u0442\u044c \u043a\u043b\u0438\u0435\u043d\u0442\u0430\u043c\u0438 \u043e\u0444\u0438\u0441\u0430', verbose_name='\u0413\u043b\u0430\u0432\u043d\u044b\u0439')),
                ('last_assigned', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0433\u043e \u0437\u0430\u043a\u0440\u0435\u043f\u043b\u0435\u043d\u0438\u044f')),
                ('can_be_auto_assigned', models.BooleanField(default=False, help_text='\u041c\u043e\u0436\u0435\u0442 \u0431\u044b\u0442\u044c \u043d\u0430\u0437\u043d\u0430\u0447\u0435\u043d \u043a\u043b\u0438\u0435\u043d\u0442\u0430\u043c \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438', verbose_name='\u0410\u0432\u0442\u043e')),
                ('allowed_ips', models.CharField(help_text='\u0420\u0430\u0437\u0440\u0435\u0448\u0451\u043d\u043d\u044b\u0435 IP-\u0430\u0434\u0440\u0435\u0441\u0430. \u041f\u0435\u0440\u0435\u0447\u0438\u0441\u043b\u044f\u0442\u044c \u0447\u0435\u0440\u0435\u0437 \u043f\u0440\u043e\u0431\u0435\u043b. \u0415\u0441\u043b\u0438 \u0443\u043a\u0430\u0437\u0430\u0442\u044c \u0437\u0434\u0435\u0441\u044c "*", \u0442\u043e \u0431\u0443\u0434\u0443\u0442 \u0440\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u044b \u043b\u044e\u0431\u044b\u0435 IP. \u041c\u043e\u0436\u043d\u043e \u0443\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043f\u043e\u0434\u0441\u0435\u0442\u0438: 192.168.1.0/25', max_length=1000, verbose_name='IP')),
                ('daily_limit', models.PositiveIntegerField(help_text='\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u043a\u043e\u043d\u0442\u0430\u043a\u0442\u043e\u0432 \u0432 \u0434\u0435\u043d\u044c \u043c\u043e\u0436\u0435\u0442 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u0435\u0442\u044c. \u0415\u0441\u043b\u0438 \u043d\u0435 \u0437\u0430\u0434\u0430\u043d\u043e, \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442\u0441\u044f \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435 \u043f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e. \u0412\u041d\u0418\u041c\u0410\u041d\u0418\u0415: \u0435\u0441\u043b\u0438 \u0443\u0432\u0435\u043b\u0438\u0447\u0438\u0432\u0430\u0435\u0442\u0435 \u044d\u0442\u043e\u0442 \u043b\u0438\u043c\u0438\u0442, \u0443\u0431\u0435\u0434\u0438\u0442\u0435\u0441\u044c, \u0447\u0442\u043e \u0443 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f \u0435\u0441\u0442\u044c \u0445\u043e\u0442\u044f \u0431\u044b \u0444\u0438\u043b\u044c\u0442\u0440\u0430\u0446\u0438\u044f \u043f\u043e IP, \u0438\u043d\u0430\u0447\u0435 \u043f\u043e\u0441\u043b\u0435\u0434\u0441\u0442\u0432\u0438\u044f \u043c\u043e\u0433\u0443\u0442 \u0431\u044b\u0442\u044c \u043f\u0435\u0447\u0430\u043b\u044c\u043d\u044b.', null=True, verbose_name='\u0414\u043d\u0435\u0432\u043d\u043e\u0439 \u043b\u0438\u043c\u0438\u0442', blank=True)),
                ('ib_account', models.PositiveIntegerField(null=True, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u043f\u0430\u0440\u0442\u043d\u0451\u0440\u0441\u043a\u043e\u0433\u043e \u0441\u0447\u0451\u0442\u0430', blank=True)),
                ('reassign_agent_code_to_office', models.BooleanField(default=False, help_text='\u0415\u0441\u043b\u0438 \u043f\u0440\u0438\u0445\u043e\u0434\u0438\u0442 \u043a\u043b\u0438\u0435\u043d\u0442 \u0441 \u043a\u043e\u0434\u043e\u043c \u0430\u0433\u0435\u043d\u0442\u0430 \u044d\u0442\u043e\u0433\u043e \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0430, \u043f\u043e\u0441\u043b\u0435 \u043d\u0430\u0437\u043d\u0430\u0447\u0435\u043d\u0438\u044f \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0430 \u0441\u043c\u0435\u043d\u0438\u0442\u044c \u043a\u043e\u0434 \u0430\u0433\u0435\u043d\u0442\u0430 \u043d\u0430 \u043a\u043e\u0434 \u0430\u0433\u0435\u043d\u0442\u0430 \u043e\u0444\u0438\u0441\u0430', verbose_name='\u041c\u0435\u043d\u044f\u0442\u044c \u043a\u043e\u0434 \u0430\u0433\u0435\u043d\u0442\u0430 \u043d\u0430 \u043e\u0444\u0438\u0441')),
                ('works_with_office_clients', models.BooleanField(default=True, help_text='\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u0441 \u043e\u0431\u044b\u0447\u043d\u044b\u043c\u0438(\u0440\u0443\u0441\u0441\u043a\u043e\u044f\u0437\u044b\u0447\u043d\u044b\u043c\u0438) \u043a\u043b\u0438\u0435\u043d\u0442\u0430\u043c\u0438 \u043e\u0444\u0438\u0441\u0430', verbose_name='\u0420\u0430\u0431\u043e\u0442\u0430\u0435\u0442 c \u043e\u0444\u0438\u0441\u043e\u043c')),
                ('works_with_english', models.BooleanField(default=False, verbose_name='\u0420\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u0441 \u0438\u043d\u043e\u0441\u0442\u0440\u0430\u043d\u043d\u044b\u043c\u0438 \u043a\u043b\u0438\u0435\u043d\u0442\u0430\u043c\u0438 \u043e\u0444\u0438\u0441\u0430')),
                ('country_state_names', models.TextField(default='', help_text='\u0414\u043b\u044f \u0442\u0435\u0445 \u0441\u043b\u0443\u0447\u0430\u0435\u0432, \u043a\u043e\u0433\u0434\u0430 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e \u0447\u0442\u043e\u0431\u044b \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0451\u043d\u043d\u044b\u0439 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0440\u0430\u0431\u043e\u0442\u0430\u043b \u0441 \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0451\u043d\u043d\u044b\u043c\u0438 \u0441\u0442\u0440\u0430\u043d\u0430\u043c\u0438/\u0440\u0435\u0433\u0438\u043e\u043d\u0430\u043c\u0438. \u041d\u0430 \u043e\u0434\u043d\u043e\u0439 \u0441\u0442\u0440\u043e\u0447\u043a\u0435, \u0447\u0435\u0440\u0435\u0437 \u0437\u0430\u043f\u044f\u0442\u0443\u044e, \u043f\u043e-\u0440\u0443\u0441\u0441\u043a\u0438.', verbose_name='\u0421\u0442\u0440\u0430\u043d\u044b/\u0440\u0435\u0433\u0438\u043e\u043d\u044b', blank=True)),
                ('sip_name', models.CharField(max_length=1000, null=True, verbose_name='SIP-\u043b\u043e\u0433\u0438\u043d', blank=True)),
                ('can_see_all_calls', models.BooleanField(default=False, verbose_name='\u041c\u043e\u0436\u0435\u0442 \u0432\u0438\u0434\u0435\u0442\u044c \u0432\u0441\u0435 \u0437\u0432\u043e\u043d\u043a\u0438')),
                ('worktime_start', models.TimeField(default=time(9, 0), help_text='\u041f\u043e \u041c\u0421\u041a', verbose_name='\u041d\u0430\u0447\u0430\u043b\u043e \u0440\u0430\u0431\u043e\u0447\u0435\u0433\u043e \u0434\u043d\u044f')),
                ('worktime_end', models.TimeField(default=time(16, 0), help_text='\u041f\u043e \u041c\u0421\u041a', verbose_name='\u041a\u043e\u043d\u0435\u0446 \u0440\u0430\u0431\u043e\u0447\u0435\u0433\u043e \u0434\u043d\u044f')),
                ('is_on_vacancies', models.BooleanField(default=False, verbose_name='\u0412 \u043e\u0442\u043f\u0443\u0441\u043a\u0435')),
                ('on_vacancies_until', models.DateField(null=True, verbose_name='\u0412 \u043e\u0442\u043f\u0443\u0441\u043a\u0435 \u0434\u043e', blank=True)),
                ('manager_page_regexp', models.CharField(help_text='\u0420\u0435\u0433\u0443\u043b\u044f\u0440\u043d\u043e\u0435 \u0432\u044b\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0434\u043b\u044f \u0441\u0442\u0440\u0430\u043d\u0438\u0446, \u043d\u0430 \u043a\u043e\u0442\u043e\u0440\u044b\u0445 \u0434\u043e\u043b\u0436\u043d\u044b \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c\u0441\u044f \u043a\u043e\u043d\u0442\u0430\u043a\u0442\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0430. \u0415\u0441\u043b\u0438 \u0432\u044b \u043d\u0435 \u0437\u043d\u0430\u0435\u0442\u0435 \u0447\u0442\u043e \u0442\u0430\u043a\u043e\u0435 "\u0440\u0435\u0433\u0443\u043b\u044f\u0440\u043d\u043e\u0435 \u0432\u044b\u0440\u0430\u0436\u0435\u043d\u0438\u0435" - \u041d\u0415 \u0422\u0420\u041e\u0413\u0410\u0419\u0422\u0415!', max_length=2000, verbose_name='\u041c\u0430\u0441\u043a\u0430 \u0441\u0442\u0440\u0430\u043d\u0438\u0446', blank=True)),
                ('amo_id', models.IntegerField(null=True, verbose_name='AmoID', blank=True)),
                ('amo_unsynced', models.BooleanField(default=True, verbose_name='\u041d\u0443\u0436\u0434\u0430\u0435\u0442\u0441\u044f \u0432 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438')),
                ('amo_synced_at', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0439 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438', blank=True)),
                ('works_with_ib', models.BooleanField(default=False, verbose_name='\u0420\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u0441 IB-\u043f\u0430\u0440\u0442\u043d\u0451\u0440\u0430\u043c\u0438')),
                ('office', models.ForeignKey(related_name='managers', verbose_name='Office', blank=True, to='crm.RegionalOffice', null=True)),
                ('substitute', models.ForeignKey(verbose_name='\u0417\u0430\u043c\u0435\u0441\u0442\u0438\u0442\u0435\u043b\u044c \u043d\u0430 \u0432\u0440\u0435\u043c\u044f \u043e\u0442\u043f\u0443\u0441\u043a\u0430', blank=True, to='crm.PersonalManager', null=True)),
                ('user', models.OneToOneField(related_name='crm_manager', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440',
                'verbose_name_plural': '\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u044b',
                'permissions': (('view_all_clients', 'Can see all clients in CRM'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlannedCall',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0432\u043e\u043d\u043a\u0430', db_index=True)),
                ('customer', models.ForeignKey(related_name='planned_calls', to='crm.CustomerRelationship')),
                ('manager', models.ForeignKey(related_name='next_calls', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'get_latest_by': 'date',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReceptionCall',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('switch_to', models.CharField(default=b'personal manager', max_length=100, verbose_name='\u041f\u0435\u0440\u0435\u0432\u0435\u0441\u0442\u0438 \u043d\u0430', choices=[(b'personal manager', '\u041f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440'), (b'tech support', '\u0422\u0435\u0445.\u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430'), (b'free education', '\u0411\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e\u0435 \u043e\u0431\u0443\u0447\u0435\u043d\u0438\u0435'), (b'fsfr', '\u0424\u0421\u0424\u0420'), (b'financial department', '\u0424\u0438\u043d\u0430\u043d\u0441\u043e\u0432\u044b\u0439 \u043e\u0442\u0434\u0435\u043b'), (b'marketing department', '\u041e\u0442\u0434\u0435\u043b \u043c\u0430\u0440\u043a\u0435\u0442\u0438\u043d\u0433\u0430'), (b'partner department', '\u041f\u0430\u0440\u0442\u043d\u0451\u0440\u0441\u043a\u0438\u0439 \u043e\u0442\u0434\u0435\u043b'), (b'tesla', '\u0422\u0435\u0441\u043b\u0430'), (b'it department', '\u041f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0438\u0441\u0442\u044b'), (b'other', '\u0414\u0440\u0443\u0433\u043e\u0435')])),
                ('name', models.CharField(max_length=250, verbose_name='\u0424\u0418\u041e', blank=True)),
                ('account', models.IntegerField(null=True, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0441\u0447\u0451\u0442\u0430', blank=True)),
                ('company', models.CharField(max_length=250, verbose_name='\u041a\u043e\u043c\u043f\u0430\u043d\u0438\u044f', blank=True)),
                ('phone', models.CharField(max_length=50, verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d', blank=True)),
                ('applied', models.BooleanField(default=False, verbose_name='\u0417\u0430\u043f\u0438\u0441\u0430\u043b\u0441\u044f \u043d\u0430 \u043e\u0431\u0443\u0447\u0435\u043d\u0438\u0435')),
                ('manager_assigned', models.BooleanField(default=False, verbose_name='\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043f\u0440\u0438\u0441\u0432\u043e\u0435\u043d \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438')),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('lesson_date', models.DateField(null=True, verbose_name='\u041d\u0430 \u043a\u0430\u043a\u043e\u0435 \u0437\u0430\u043f\u0438\u0441\u0430\u043b\u0441\u044f', blank=True)),
                ('experienced', models.BooleanField(default=False, verbose_name='\u0421 \u043e\u043f\u044b\u0442\u043e\u043c')),
            ],
            options={
                'permissions': (('reception_call', 'Allows access to reception call form'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='crmcomment',
            name='customer',
            field=models.ForeignKey(related_name='comments', to='crm.CustomerRelationship'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='callinfo',
            name='customer',
            field=models.ForeignKey(related_name='calls', to='crm.CustomerRelationship'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brocomt4account',
            name='user',
            field=models.ForeignKey(related_name='accounts', to='crm.BrocoUser'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accountdataview',
            name='customer',
            field=models.ForeignKey(related_name='data_views', to='crm.CustomerRelationship'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accountdataview',
            name='user',
            field=models.ForeignKey(verbose_name='\u041a\u0442\u043e \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u0435\u043b', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='_phones',
            field=models.TextField(
                help_text='\u041a\u0430\u0436\u0434\u044b\u0439 \u0442\u0435\u0435\u043b\u0444\u043e\u043d \u043d\u0430 \u043d\u043e\u0432\u043e\u0439 \u0441\u0442\u0440\u043e\u043a\u0435',
                max_length=1024,
                verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d\u044b \u043e\u0444\u0438\u0441\u0430',
                blank=True),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='regionaloffice',
            name='phone',
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='address_pl',
            field=models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='caption_pl',
            field=models.CharField(max_length=150, null=True,
                                   verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='metro_pl',
            field=models.CharField(
                help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='name_pl',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='address_pt',
            field=models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='caption_pt',
            field=models.CharField(max_length=150, null=True,
                                   verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='metro_pt',
            field=models.CharField(
                help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='name_pt',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434'),
        ),
        migrations.AlterField(
            model_name='regionaloffice',
            name='email',
            field=models.EmailField(max_length=254, null=True,
                                    verbose_name='E-mail \u043e\u0444\u0438\u0441\u0430 (\u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0439)',
                                    blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='address_ar',
            field=models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='caption_ar',
            field=models.CharField(max_length=150, null=True,
                                   verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='metro_ar',
            field=models.CharField(
                help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='name_ar',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434'),
        ),
        migrations.AlterField(
            model_name='regionaloffice',
            name='emails',
            field=models.CharField(default=b'partner.global@grandcapital.net',
                                   help_text='\u0447\u0435\u0440\u0435\u0437 \u0437\u0430\u043f\u044f\u0442\u0443\u044e',
                                   max_length=255,
                                   verbose_name="Email'\u044b, \u043d\u0430 \u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u0441\u043b\u0430\u0442\u044c \u0437\u0430\u043f\u0440\u043e\u0441\u044b \u043d\u0430 \u043e\u0431\u0443\u0447\u0435\u043d\u0438\u0435"),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='address_fa',
            field=models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='address_fr',
            field=models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='address_hy',
            field=models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='address_ka',
            field=models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='address_th',
            field=models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='address_uk',
            field=models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='caption_fa',
            field=models.CharField(max_length=150, null=True,
                                   verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='caption_fr',
            field=models.CharField(max_length=150, null=True,
                                   verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='caption_hy',
            field=models.CharField(max_length=150, null=True,
                                   verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='caption_ka',
            field=models.CharField(max_length=150, null=True,
                                   verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='caption_th',
            field=models.CharField(max_length=150, null=True,
                                   verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='caption_uk',
            field=models.CharField(max_length=150, null=True,
                                   verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='metro_fa',
            field=models.CharField(
                help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='metro_fr',
            field=models.CharField(
                help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='metro_hy',
            field=models.CharField(
                help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='metro_ka',
            field=models.CharField(
                help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='metro_th',
            field=models.CharField(
                help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='metro_uk',
            field=models.CharField(
                help_text='\u0415\u0441\u043b\u0438 \u0432 \u0433\u043e\u0440\u043e\u0434\u0435 \u043d\u0435\u0442 \u043c\u0435\u0442\u0440\u043e - \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c',
                max_length=255, null=True, verbose_name='\u041c\u0435\u0442\u0440\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='name_fa',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='name_fr',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='name_hy',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='name_ka',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='name_th',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434'),
        ),
        migrations.AddField(
            model_name='regionaloffice',
            name='name_uk',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434'),
        ),
    ]
