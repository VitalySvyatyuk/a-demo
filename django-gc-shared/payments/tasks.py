# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from celery.task import task


def update_qiwi_statuses():
    """Go to Qiwi XML Api and update all statuses"""
    from payments.systems.qiwi import DepositForm
    return DepositForm.update_status()


# кэшируем на один день
TIMEOUT = timedelta(1)
CELERY_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def update_profit(obj):
    profile = obj.account.user.profile

    if not (profile.params and profile.params.get("last_updated")):
        # по умолчанию, запрос помечен на обновление
        if not profile.params:
            profile.params = {}
        profile.params["last_updated"] = (datetime.now()-TIMEOUT).strftime(CELERY_TIME_FORMAT)
        profile.save()

    last_updated = datetime.strptime(profile.params["last_updated"], CELERY_TIME_FORMAT)

    if datetime.now() - last_updated < TIMEOUT:
        return

    # если с celery что-то случится, то при запросе обновления через 10 минут - обновление произойдет
    profile.params["last_updated"] = (last_updated + timedelta(minutes=10)).strftime(CELERY_TIME_FORMAT)
    profile.save()
    update_profitability.delay(obj.id)
    return


@task
def update_profitability(request_id):

    from payments.models import WithdrawRequest

    account = WithdrawRequest.objects.get(id=request_id).account
    profile = account.user.profile

    totals = account.totals_all_accounts

    if totals is not None:
        profit = totals["profit"] if "profit" in totals else 0
        profitability_deposit = (totals['profitability_deposit']
                                 if 'profitability_deposit' in totals else 0)
    else:
        profit = None
        profitability_deposit = 0

    profile.params["profit"] = profit
    profile.params["profitability_deposit"] = profitability_deposit
    profile.params["last_updated"] = datetime.now().strftime(CELERY_TIME_FORMAT)
    profile.save()
