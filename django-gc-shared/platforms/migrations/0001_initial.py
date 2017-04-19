# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import shared.utils


class Migration(migrations.Migration):

    operations = [
        migrations.CreateModel(
            name='TradingAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mt4_id', models.IntegerField(help_text='Account ID at the trading platform', verbose_name='Account id', db_column=b'mt4_id', db_index=True)),
                ('group_name', models.CharField(max_length=50, null=True, verbose_name='Account type', db_column=b'_group', blank=True)),
                ('creation_ts', models.DateTimeField(default=datetime.datetime.now, verbose_name='Creation timestamp')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Account deleted')),
                ('is_archived', models.BooleanField(default=False, help_text='Account was automatically archived', verbose_name='Account is archived')),
                ('deleted_comment', models.TextField(null=True, verbose_name='Deletion reason', blank=True)),
                ('client_agreement', models.FileField(null=True, upload_to=shared.utils.UploadTo(b'client_agreements'), blank=True)),
                ('partner_agreement', models.FileField(null=True, upload_to=shared.utils.UploadTo(b'partner_agreements'), blank=True)),
                ('is_fully_withdrawn', models.BooleanField(default=False, verbose_name='Fully withdrawn', editable=False)),
                ('last_block_reason', models.CharField(blank=True, max_length=200, null=True, verbose_name='Last block reason', choices=[(b'Doc. verification failed', b'Doc. verification failed'), (b'Needs deposit verification', b'Needs deposit verification')])),
                ('previous_agent_account', models.PositiveIntegerField(help_text=b'Used to return to previous IB', null=True, editable=False, blank=True)),
                ('is_agreed_managed', models.BooleanField(default=False, verbose_name='Investment agreement accepted')),
                ('qualified_for_own_reward', models.BooleanField(default=False, help_text='Only for IBs. During the last verification, this partner could receive IB commission for own accs', editable=False)),
                ('agreement_type', models.CharField(default=None, choices=[(b'simple_with_documents', '\u041f\u0440\u043e\u0441\u0442\u043e\u0435 \u043f\u043e\u0434\u043f\u0438\u0441\u0430\u043d\u0438\u0435, \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u044b \u0447\u0435\u0440\u0435\u0437 \u0444\u043e\u0440\u043c\u0443 \u043d\u0430 \u0441\u0430\u0439\u0442\u0435'), (b'simple_no_documents', '\u041f\u0440\u043e\u0441\u0442\u043e\u0435 \u043f\u043e\u0434\u043f\u0438\u0441\u0430\u043d\u0438\u0435, \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b \u0443\u0436\u0435 \u0432 \u043e\u0444\u0438\u0441\u0435'), (b'oferta', '\u0421\u043e\u0433\u043b\u0430\u0441\u0438\u0435 \u0441 \u043e\u0444\u0435\u0440\u0442\u043e\u0439')], max_length=70, blank=True, null=True, verbose_name='Agreement type')),
                ('platform_type', models.CharField(default=b'mt4', max_length=70, verbose_name='Trading platform type', choices=[(b'mt4', 'Meta Trader 4, https://support.metaquotes.net/ru/docs/mt4/api/server_api'), (b'cfh', 'CFH, http://www.cfhclearing.com/back-office-api/'), (b'strategy_store', 'StrategyStore, http://strategystore.org/')])),
            ],
            options={
                'ordering': ['mt4_id', 'group_name'],
            },
        ),
    ]
