# coding=utf-8
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import activate, ugettext_lazy as _

from mt4.models import Mt4User, Mt4Account
from sms import send_with_check_verification, send
from sms.models import SMSMessage


class Command(BaseCommand):
    def handle(self, *args, **options):
        margin_call_accs = set(Mt4User.objects.filter(margin_level__range=(80, 100)).values_list('login', flat=True))

        for acc_id in margin_call_accs:
            if SMSMessage.objects.filter(params__reason="margincall", params__acc=acc_id,
                                         timestamp__gt=datetime.now() - timedelta(days=1)).exists():
                continue
            mt4_acc = Mt4Account.objects.filter(mt4_id=acc_id).first()
            if not mt4_acc:
                continue

            profile = mt4_acc.user.profile

            # time = profile.get_local_time() or datetime.now()
            # if not (7 < time.hour < 22):
            #     continue

            if profile.country and profile.country.language in settings.LANGUAGE_CODES:
                activate(profile.country.language)
            else:
                activate("en")

            result = send(
                profile.phone_mobile,
                text=_("Warning! Account %d is close to the margin call! We recommend you to top up the account to "
                       "prevent your trades from being forcibly closed. GMI") % acc_id,
                params={"reason": "margincall", "acc": unicode(acc_id)},
            )
            # if result and profile.manager:
            #     mt4_acc.user.gcrm_contact.add_task(text=_(u"SMS-warning about margin call was sent on account number "
            #                                               u"%d") % acc_id, notify=True)
