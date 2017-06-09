from django.core.management import BaseCommand
from notification import models as notification
from datetime import datetime, timedelta
from payments.models import WithdrawRequest


class Command(BaseCommand):
    '''
    Command to inform users about ongoing withdrawal.
    Execute with "0 */1 * * * "   else change end_time in send_by_hours
    '''
    def execute(self, *args, **options):
        self.send_by_hours(60, 'withdraw_processing_verified')
        self.send_by_hours(84, 'withdraw_processing_in_finance')
        self.send_by_hours(108, 'withdraw_processing_transfer_ready')

    def send_by_hours(self, hours, template):
        start_time = datetime.now() - timedelta(hours=hours)
        end_time = datetime.now() - timedelta(hours=hours-1, microseconds=1)  # interval hour

        requests = WithdrawRequest.objects.filter(
            creation_ts__range=(start_time, end_time),
            is_committed=None)
        for request in requests:
            notification.send([request.account.user], template, {
                'account_id': request.account.mt4_id,
                'amount_money': request.amount_money,
                'payment_system': request.payment_system,
            })
