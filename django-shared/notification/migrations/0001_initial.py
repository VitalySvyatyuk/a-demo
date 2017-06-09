# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import project.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MessageTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Template name')),
                ('subject', models.CharField(help_text="The default subject if a campaign doesn't specify it", max_length=255, verbose_name='Subject')),
                ('text', models.TextField(help_text='Available variables: current_site, domain, unsubscribe_url, browser_url, subject', null=True, verbose_name='Plaintext message', blank=True)),
                ('html', models.TextField(help_text='Available variables: current_site, domain, unsubscribe_url, browser_url, subject', null=True, verbose_name='HTML message', blank=True)),
                ('language', project.fields.LanguageField(default=b'ru', max_length=10, verbose_name='Language', db_index=True, choices=[(b'ru', b'Russian'), (b'en', b'English')])),
            ],
            options={
                'verbose_name': 'Message template',
                'verbose_name_plural': 'Message templates',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notification_type', models.CharField(max_length=2048, verbose_name='\u0422\u0438\u043f \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f', choices=[(b'deposit_needs_verification', '\u0412\u0432\u043e\u0434 \u043d\u0443\u0436\u0434\u0430\u0435\u0442\u0441\u044f \u0432 \u0432\u0435\u0440\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438'), (b'deposit_request_committed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u0432\u043e\u0434 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430'), (b'deposit_request_created', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u0432\u043e\u0434 \u0441\u043e\u0437\u0434\u0430\u043d\u0430'), (b'deposit_request_failed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u0432\u043e\u0434 \u043d\u0435 \u0443\u0434\u0430\u043b\u0430\u0441\u044c'), (b'withdraw_processing_in_finance', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0432 \u0431\u0443\u0445\u0433\u0430\u043b\u0442\u0435\u0440\u0438\u0438'), (b'withdraw_processing_transfer_ready', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0433\u043e\u0442\u043e\u0432\u0430 \u043a \u043f\u0435\u0440\u0435\u0432\u043e\u0434\u0443'), (b'withdraw_processing_verified', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0432\u0435\u0440\u0438\u0444\u0438\u0446\u0438\u0440\u043e\u0432\u0430\u043d\u0430'), (b'withdraw_request_committed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430'), (b'withdraw_request_created', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0441\u043e\u0437\u0434\u0430\u043d\u0430'), (b'withdraw_request_failed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u043d\u0435 \u0443\u0434\u0430\u043b\u0430\u0441\u044c'), (b'account_unblock', '\u0421\u0447\u0435\u0442 \u0440\u0430\u0437\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d'), (b'account_unblock_rejected', '\u041e\u0442\u043a\u0430\u0437\u0430\u043d\u043e \u0432 \u0440\u0430\u0437\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0435 \u0441\u0447\u0435\u0442\u0430'), (b'checkdocument_issue', '\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u043e\u0432'), (b'internaltransfer_issue', '\u0412\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0439 \u043f\u0435\u0440\u0435\u0432\u043e\u0434'), (b'user_issue', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0443'), (b'document_verified', '\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442 \u043e\u0434\u043e\u0431\u0440\u0435\u043d'), (b'account_created', '\u0421\u0447\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u043d'), (b'leverage_change', '\u041f\u043b\u0435\u0447\u043e \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e'), (b'password_recovery', '\u041f\u0430\u0440\u043e\u043b\u044c \u0432\u043e\u0441\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d'), (b'realib_account_created', 'real IB \u0441\u0447\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u043d'), (b'report_generation_failed', '\u041e\u0448\u0438\u0431\u043a\u0430 \u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u0438 \u043e\u0442\u0447\u0435\u0442\u0430'), (b'report_has_been_generated', '\u041e\u0442\u0447\u0435\u0442 \u0431\u044b\u043b \u0441\u0433\u0435\u043d\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u043d'), (b'manual_transfer_submitted', '\u0423\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u0435 \u043e \u0432\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0435\u043c \u043f\u0435\u0440\u0435\u0432\u043e\u0434\u0435'), (b'friend_recommendation', '\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u044f \u0434\u0440\u0443\u0433\u0443')])),
                ('language', models.CharField(default=b'ru', max_length=10, verbose_name=b'Language', choices=[(b'ru', b'Russian'), (b'en', b'English')])),
                ('published', models.BooleanField(default=False, help_text='\u0415\u0441\u043b\u0438 \u043d\u0435 \u043e\u043f\u0443\u0431\u043b\u0438\u043a\u043e\u0432\u0430\u043d\u043e, \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c\u0441\u044f \u043d\u0435 \u0431\u0443\u0434\u0435\u0442', verbose_name='\u041e\u043f\u0443\u0431\u043b\u0438\u043a\u043e\u0432\u0430\u043d\u0430')),
                ('send_in_private', models.BooleanField(default=True, verbose_name='\u041e\u0442\u043f\u0440\u0430\u0432\u043b\u044f\u0442\u044c \u0432 \u041b\u0438\u0447\u043d\u044b\u0439 \u043a\u0430\u0431\u0438\u043d\u0435\u0442/\u041c\u043e\u0438 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f')),
                ('email_subject', models.CharField(max_length=255, verbose_name='\u0422\u0435\u043c\u0430 \u043f\u0438\u0441\u044c\u043c\u0430')),
                ('html', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f')),
            ],
            options={
                'verbose_name': '\u0423\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u0423\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='NotificationSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(default=b'ru', unique=True, max_length=10, verbose_name=b'Language', choices=[(b'ru', b'Russian'), (b'en', b'English')])),
                ('default_notification_template', models.ForeignKey(verbose_name='\u0428\u0430\u0431\u043b\u043e\u043d \u043f\u0438\u0441\u044c\u043c\u0430', to='notification.MessageTemplate')),
            ],
            options={
                'verbose_name': '\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043e\u043f\u043e\u0432\u0435\u0449\u0435\u043d\u0438\u0439',
                'verbose_name_plural': '\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043e\u043f\u043e\u0432\u0435\u0449\u0435\u043d\u0438\u0439',
            },
        ),
        migrations.AlterUniqueTogether(
            name='notification',
            unique_together=set([('notification_type', 'language')]),
        ),
    ]
