# coding=utf-8

from celery.app import default_app
from celery.task import task
from djcelery.backends.cache import CacheBackend

from log.models import Logger, Events
from platforms.mt4 import mt4api
from platforms.models import TradingAccount
from platforms.signals import account_created
from platforms.types import (get_account_type)
from referral.models import PartnerDomain


@task(backend=CacheBackend(default_app), time_limit=120)
def register_mt4account(details, user, account_type_details, form_class, partner_api_id, additional_fields=None):
    additional_fields = additional_fields or dict()
    engine = "demo" if account_type_details["is_demo"] else "default"
    mt4_id = mt4api.RemoteMT4Manager(engine).create_account(**details)
    # mt4_id = api.SocketAPI(engine=account_type_details['engine']).create_account(**details)
    account = TradingAccount(user=user,
                         mt4_id=mt4_id,
                         group_name=account_type_details['slug'],
                         agreement_type=additional_fields.get('agreement_type'))

    if partner_api_id:
        try:
            account.registered_from_partner_domain = PartnerDomain.objects.get(api_key=partner_api_id)
        except PartnerDomain.DoesNotExist:
            pass

    account.save()

    Logger(user=user, content_object=account, ip=account_type_details["ip"], event=Events.ACCOUNT_CREATED).save()
    form_class.send_notification(account, account_type_details['slug'], **details)

    account_created.send(
        sender=account,
        type_details=account_type_details,
        mt4data=details,
    )

    account_group = get_account_type(account_type_details['slug'])
    if account_group.creation_callback is not None:
        account_group.creation_callback(account, **additional_fields)

    return {'mt4_id': mt4_id, 'mt4_password': details['password'], 'slug': account_type_details['slug'], 'account_pk': account.pk}