# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import payments.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('symbol', models.CharField(max_length=100, verbose_name='Transaction type')),
                ('comment', models.CharField(max_length=100, verbose_name='Comment')),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=10, decimal_places=2)),
                ('currency', models.CharField(max_length=6, null=True, verbose_name='Currency', choices=[(b'RUR', b'RUR'), (b'USD', b'USD'), (b'EUR', b'EUR')])),
                ('trade_id', models.CharField(max_length=20, null=True, verbose_name='Trade ID', blank=True)),
            ],
            options={
                'verbose_name': '\u0440\u0443\u0447\u043d\u0430\u044f \u0442\u0440\u0430\u043d\u0437\u0430\u043a\u0446\u0438\u044f',
                'verbose_name_plural': '\u0440\u0443\u0447\u043d\u044b\u0435 \u0442\u0440\u0430\u043d\u0437\u0430\u043a\u0446\u0438\u0438',
            },
        ),
        migrations.CreateModel(
            name='BaseRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(help_text='Example: 5.2', verbose_name='Amount', max_digits=10, decimal_places=2)),
                ('conversion_rate', models.FloatField(null=True, verbose_name='Exchange rate at request date', blank=True)),
                ('payment_system', payments.fields.PaymentSystemField(default='', max_length=50, verbose_name='Payment system')),
                ('active_balance', models.DecimalField(decimal_places=2, editable=False, max_digits=10, blank=True, help_text='Balance on getting request', null=True, verbose_name='Balance')),
                ('currency', models.CharField(max_length=6, verbose_name='Currency', choices=[(b'RUR', b'RUR'), (b'USD', b'USD'), (b'EUR', b'EUR')])),
                ('private_comment', models.TextField(null=True, verbose_name='Internal comment', blank=True)),
                ('public_comment', models.TextField(null=True, verbose_name='Public comment', blank=True)),
                ('comment_visible', models.BooleanField(default=True, verbose_name="Manager's comment is shown to client")),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='Creation timestamp', db_index=True)),
                ('trade_id', models.CharField(max_length=20, null=True, verbose_name='Trade ID', blank=True)),
                ('params', jsonfield.fields.JSONField(null=True, verbose_name='Details', blank=True)),
                ('is_payed', models.NullBooleanField(verbose_name='Is payed')),
                ('is_committed', models.NullBooleanField(help_text='When this field changes, client gets a notification', verbose_name='Is committed')),
                ('_is_automatic', models.BooleanField(default=False, verbose_name='Automatically')),
            ],
            options={
                'ordering': ['-creation_ts'],
                'get_latest_by': 'creation_ts',
            },
        ),
        migrations.CreateModel(
            name='TypicalComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('public', models.BooleanField(default=False)),
                ('for_deposit', models.BooleanField(default=True)),
                ('for_withdraw', models.BooleanField(default=False)),
                ('is_rus', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('-is_rus', '-creation_ts'),
            },
        ),
        migrations.CreateModel(
            name='WithdrawRequestsGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_closed', models.BooleanField(default=False, verbose_name='Closed')),
                ('processing_level', models.IntegerField(default=0)),
                ('processing_departments', models.CharField(default='', max_length=500, verbose_name='Departments')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
            ],
            options={
                'verbose_name': 'Withdraw request group',
                'verbose_name_plural': 'Withdraw request groups',
                'permissions': (('can_edit_approvals', 'Can edit approvals'),),
            },
        ),
        migrations.CreateModel(
            name='WithdrawRequestsGroupApproval',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_accepted', models.BooleanField(default=False, verbose_name='Is accepted')),
                ('comment', models.TextField(null=True, verbose_name='Comment', blank=True)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('group', models.ForeignKey(related_name='approvals', verbose_name='Withdraw Requests Group', to='payments.WithdrawRequestsGroup', null=True)),
                ('updated_by', models.ForeignKey(related_name='+', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(help_text='Who made decision', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DepositRequest',
            fields=[
                ('baserequest_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='payments.BaseRequest')),
                ('old_id', models.IntegerField(null=True, blank=True)),
                ('purse', models.CharField(max_length=50, null=True, verbose_name='Purse', blank=True)),
            ],
            options={
                'ordering': ['-creation_ts', 'payment_system'],
                'verbose_name': 'Deposit request',
                'verbose_name_plural': 'Deposit requests',
            },
            bases=('payments.baserequest',),
        ),
        migrations.CreateModel(
            name='WithdrawRequest',
            fields=[
                ('baserequest_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='payments.BaseRequest')),
                ('old_id', models.IntegerField(null=True, blank=True)),
                ('reason', models.CharField(choices=[('funds', 'Withdraw the funds I earn'), ('money', 'In need of money'), ('service', 'Not satisfied with the service'), ('other', 'Other reasons')], max_length=50, blank=True, help_text='Choose the reason of withdrawal', null=True, verbose_name='Reason of withdrawal')),
                ('is_ready_for_payment', models.BooleanField(default=False, verbose_name='Is ready for payout')),
            ],
            options={
                'ordering': ['-creation_ts', 'requisit'],
                'verbose_name': 'Withdraw request',
                'verbose_name_plural': 'Withdraw requests',
            },
            bases=('payments.baserequest',),
        ),
    ]
