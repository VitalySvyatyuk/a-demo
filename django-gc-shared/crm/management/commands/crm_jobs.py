# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _


class Command(BaseCommand):
    def execute(self, *args, **options):
        create_stale_deposit_requests_tasks()
        create_wb500_tasks()


def create_stale_deposit_requests_tasks():
    from payments.models import DepositRequest
    qs = DepositRequest.objects.filter(
        is_payed=None,
        is_committed=None,
        creation_ts__gte=datetime.now()-timedelta(days=1),
        creation_ts__lte=datetime.now()-timedelta(minutes=20))

    for req in qs:
        profile = req.account.user.profile
        text = _(u"According to the deposit request id{r.id}({r.payment_system} {r.amount_money!s}) on account "
                 u"{r.account} from {r.creation_ts:%Y/%m/%d %H:%M:%S} the funds haven't been deposited yet")
        text = text.format(r=req)
        if not profile.manager:
            profile.autoassign_manager(True)
            profile.save()

        from gcrm.models import Task
        if profile.manager and not Task.objects.filter(contact=req.account.user.gcrm_contact, text=text).exists():
            req.account.user.gcrm_contact.add_task(text=text, at=timedelta(minutes=20))


def create_wb500_tasks():
    from crm.utils import is_spb_school_client
    from bonus.models import WelcomeBonus
    for wb in WelcomeBonus.objects.filter(amount=500, account___group__in=("realstd_us_me", "realmic_us_me")):
        if is_spb_school_client(wb.account.user.profile):
            continue
        mt4_user = wb.account.get_mt4user()
        if not mt4_user or mt4_user.equity <= 0:
            continue
        user = wb.account.user
        text = _(u"Motivate to deposit Welcome Bonus 500 (account %d)") % wb.account.mt4_id

        if not user.profile.manager:
            user.profile.autoassign_manager(True)
            user.profile.save()

        from gcrm.models import Task
        if user.profile.manager and not Task.objects.filter(contact=user.gcrm_contact, text=text).exists():
            user.gcrm_contact.add_task(text=text)
