# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0007_auto_20170120_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(max_length=2048, verbose_name='Notification type', choices=[(b'user_registered', 'User registered'), (b'deposit_needs_verification', 'Deposit need verification'), (b'deposit_request_committed', 'Deposit request committed'), (b'deposit_request_created', 'Deposit request created'), (b'deposit_request_failed', 'Deposit request failed'), (b'withdraw_processing_in_finance', 'Withdraw processing in finance'), (b'withdraw_processing_transfer_ready', 'Withdraw processing transfer ready'), (b'withdraw_processing_verified', 'Withdraw processing verified'), (b'withdraw_request_committed', 'Withdraw request committed'), (b'withdraw_request_created', 'Withdraw request created'), (b'withdraw_request_failed', 'Withdraw request failed'), (b'account_unblock', 'Account unblock'), (b'account_unblock_rejected', 'Account unblock rejected'), (b'checkdocument_issue', 'Checking documents'), (b'internaltransfer_issue', 'Internal transfer'), (b'user_issue', 'Support request'), (b'document_verified', 'Document verified'), (b'account_created', 'Account created'), (b'leverage_change', 'Leverage changed'), (b'password_recovery', 'Password recovered'), (b'realib_account_created', 'real IB account created'), (b'report_generation_failed', 'Report generation failed'), (b'report_has_been_generated', 'Report generation finished'), (b'webinar_2days_reminder', '2 day until webinar starts'), (b'webinar_has_record', 'Webinar has record'), (b'webinar_link_to_record_changed', 'Webinar link to record changed'), (b'webinar_registration', 'Webinar registration'), (b'webinar_today_reminder', 'Webinar starts today'), (b'callback_request', 'Callback request'), (b'manual_transfer_submitted', 'Internal transfer'), (b'friend_recommendation', 'Friend recomendation')]),
        ),
    ]
