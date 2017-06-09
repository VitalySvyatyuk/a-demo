# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import geobase.phone_code_widget
import project.validators


class Migration(migrations.Migration):

    dependencies = [
        ('issuetracker', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('platforms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountVerification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('verified', models.BooleanField(default=True, verbose_name='\u041f\u0440\u043e\u0432\u0435\u0440\u0435\u043d')),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('account', models.OneToOneField(related_name='verification', verbose_name='\u0421\u0447\u0435\u0442', to='platforms.TradingAccount', help_text='\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0441\u0447\u0435\u0442 Real IB')),
            ],
            options={
                'verbose_name': '\u0412\u0435\u0440\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u044f \u0441\u0447\u0435\u0442\u0430',
                'verbose_name_plural': '\u0412\u0435\u0440\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438 \u0441\u0447\u0435\u0442\u043e\u0432',
            },
        ),
        migrations.CreateModel(
            name='Click',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('agent_code', models.IntegerField(verbose_name='Agent code')),
                ('date', models.DateField(auto_now=True)),
                ('clicks', models.IntegerField(default=0, verbose_name='Click count')),
                ('partner_domain_requests', models.IntegerField(default=0, verbose_name='\u041a\u043e\u043b-\u0432\u043e \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u043e\u0432 \u043f\u0430\u0440\u0442\u043d\u0451\u0440\u0441\u043a\u0438\u0445 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u043e\u0432')),
                ('unique_clicks', models.IntegerField(default=0, verbose_name='Unique click count')),
            ],
            options={
                'verbose_name': 'Agent code click',
                'verbose_name_plural': 'Agent code clicks',
            },
        ),
        migrations.CreateModel(
            name='PartnerCertificateIssue',
            fields=[
                ('genericissue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='issuetracker.GenericIssue')),
                ('partner_account_number', models.PositiveIntegerField(null=True, verbose_name='\u041f\u0430\u0440\u0442\u043d\u0435\u0440\u0441\u043a\u0438\u0439 \u0441\u0447\u0435\u0442', blank=True)),
                ('tel_numb', models.CharField(max_length=40, null=True, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0430', blank=True)),
            ],
            options={
                'verbose_name': '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u0430',
                'verbose_name_plural': '\u0417\u0430\u044f\u0432\u043a\u0438 \u043d\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u0430',
            },
            bases=('issuetracker.genericissue',),
        ),
        migrations.CreateModel(
            name='PartnerDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(db_index=True, max_length=73, validators=[project.validators.DomainValidator()])),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('api_key', models.CharField(unique=True, max_length=40, db_index=True)),
                ('account', models.ForeignKey(related_name='partner_domains', to=settings.AUTH_USER_MODEL)),
                ('ib_account', models.ForeignKey(to='platforms.TradingAccount')),
            ],
            options={
                'verbose_name': 'Partner domain',
            },
        ),
        migrations.CreateModel(
            name='PartnershipApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Your name')),
                ('phone', geobase.phone_code_widget.CountryPhoneCodeField(max_length=40, verbose_name='Phone number')),
                ('email', models.EmailField(max_length=254, verbose_name='E-mail')),
                ('partnership_type', models.CharField(max_length=20, verbose_name='\u0422\u0438\u043f \u043f\u0430\u0440\u0442\u043d\u0451\u0440\u0441\u0442\u0432\u0430')),
            ],
            options={
                'verbose_name': '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u043f\u0430\u0440\u0442\u043d\u0451\u0440\u0441\u0442\u0432\u043e',
                'verbose_name_plural': '\u0417\u0430\u044f\u0432\u043a\u0438 \u043d\u0430 \u043f\u0430\u0440\u0442\u043d\u0451\u0440\u0441\u0442\u0432\u043e',
            },
        ),
        migrations.AlterUniqueTogether(
            name='click',
            unique_together=set([('agent_code', 'date')]),
        ),
    ]
