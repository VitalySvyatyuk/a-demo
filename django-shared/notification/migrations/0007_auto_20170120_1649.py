# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0006_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'verbose_name': 'Notification', 'verbose_name_plural': 'Notifications'},
        ),
        migrations.AlterModelOptions(
            name='notificationsettings',
            options={'verbose_name': 'Notification options', 'verbose_name_plural': 'Notifications options'},
        ),
        migrations.AlterField(
            model_name='notification',
            name='duplicate_by_sms',
            field=models.BooleanField(default=False, verbose_name='Duplicate by SMS?'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='email_subject',
            field=models.CharField(max_length=255, verbose_name='Letter subject'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='html',
            field=models.TextField(verbose_name='Notification text'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(max_length=2048, verbose_name='Notification type', choices=[(b'user_registered', 'User registered'), (b'deposit_needs_verification', '\u0412\u0432\u043e\u0434 \u043d\u0443\u0436\u0434\u0430\u0435\u0442\u0441\u044f \u0432 \u0432\u0435\u0440\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438'), (b'deposit_request_committed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u0432\u043e\u0434 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430'), (b'deposit_request_created', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u0432\u043e\u0434 \u0441\u043e\u0437\u0434\u0430\u043d\u0430'), (b'deposit_request_failed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u0432\u043e\u0434 \u043d\u0435 \u0443\u0434\u0430\u043b\u0430\u0441\u044c'), (b'withdraw_processing_in_finance', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0432 \u0431\u0443\u0445\u0433\u0430\u043b\u0442\u0435\u0440\u0438\u0438'), (b'withdraw_processing_transfer_ready', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0433\u043e\u0442\u043e\u0432\u0430 \u043a \u043f\u0435\u0440\u0435\u0432\u043e\u0434\u0443'), (b'withdraw_processing_verified', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0432\u0435\u0440\u0438\u0444\u0438\u0446\u0438\u0440\u043e\u0432\u0430\u043d\u0430'), (b'withdraw_request_committed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430'), (b'withdraw_request_created', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0441\u043e\u0437\u0434\u0430\u043d\u0430'), (b'withdraw_request_failed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u043d\u0435 \u0443\u0434\u0430\u043b\u0430\u0441\u044c'), (b'account_unblock', '\u0421\u0447\u0435\u0442 \u0440\u0430\u0437\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d'), (b'account_unblock_rejected', '\u041e\u0442\u043a\u0430\u0437\u0430\u043d\u043e \u0432 \u0440\u0430\u0437\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0435 \u0441\u0447\u0435\u0442\u0430'), (b'checkdocument_issue', '\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u043e\u0432'), (b'internaltransfer_issue', '\u0412\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0439 \u043f\u0435\u0440\u0435\u0432\u043e\u0434'), (b'user_issue', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0443'), (b'document_verified', '\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442 \u043e\u0434\u043e\u0431\u0440\u0435\u043d'), (b'account_created', '\u0421\u0447\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u043d'), (b'leverage_change', '\u041f\u043b\u0435\u0447\u043e \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e'), (b'password_recovery', '\u041f\u0430\u0440\u043e\u043b\u044c \u0432\u043e\u0441\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d'), (b'realib_account_created', 'real IB \u0441\u0447\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u043d'), (b'report_generation_failed', '\u041e\u0448\u0438\u0431\u043a\u0430 \u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u0438 \u043e\u0442\u0447\u0435\u0442\u0430'), (b'report_has_been_generated', '\u041e\u0442\u0447\u0435\u0442 \u0431\u044b\u043b \u0441\u0433\u0435\u043d\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u043d'), (b'webinar_2days_reminder', '\u0414\u043e \u0432\u0435\u0431\u0438\u043d\u0430\u0440\u0430 \u043e\u0441\u0442\u0430\u043b\u043e\u0441\u044c 2 \u0434\u043d\u044f'), (b'webinar_has_record', '\u0412\u0435\u0431\u0438\u043d\u0430\u0440 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d'), (b'webinar_link_to_record_changed', '\u0418\u0437\u043c\u0435\u043d\u0438\u043b\u0430\u0441\u044c \u0441\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 \u0437\u0430\u043f\u0438\u0441\u044c \u0432\u0435\u0431\u0438\u043d\u0430\u0440\u0430'), (b'webinar_registration', '\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f \u043d\u0430 \u0432\u0435\u0431\u0438\u043d\u0430\u0440'), (b'webinar_today_reminder', '\u0412\u0435\u0431\u0438\u043d\u0430\u0440 \u043f\u0440\u043e\u0432\u043e\u0434\u0438\u0442\u0441\u044f \u0441\u0435\u0433\u043e\u0434\u043d\u044f'), (b'callback_request', '\u041f\u0440\u043e\u0441\u044c\u0431\u0430 \u043e\u0431\u0440\u0430\u0442\u043d\u043e\u0433\u043e \u0437\u0432\u043e\u043d\u043a\u0430'), (b'manual_transfer_submitted', '\u0423\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u0435 \u043e \u0432\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0435\u043c \u043f\u0435\u0440\u0435\u0432\u043e\u0434\u0435'), (b'friend_recommendation', '\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u044f \u0434\u0440\u0443\u0433\u0443')]),
        ),
        migrations.AlterField(
            model_name='notification',
            name='published',
            field=models.BooleanField(default=False, help_text='If not published, it will not be used', verbose_name='Published'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='send_in_private',
            field=models.BooleanField(default=True, verbose_name='Send to private office/ My messages'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='text',
            field=models.TextField(help_text='8 messages max', null=True, verbose_name='SMS text', blank=True),
        ),
        migrations.AlterField(
            model_name='notificationsettings',
            name='default_notification_template',
            field=models.ForeignKey(verbose_name='Letter template', to='notification.MessageTemplate'),
        ),
    ]
