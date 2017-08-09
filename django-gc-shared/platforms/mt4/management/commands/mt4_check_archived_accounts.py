from django.core.management import BaseCommand

from platforms.models import TradingAccount
from platforms.mt4.external.models_users import ArchiveUser
from platforms.mt4.external.models_users import DemoUser
from platforms.mt4.external.models_users import RealUser


# noinspection PyAbstractClass
class Command(BaseCommand):
    def execute(self, *args, **options):
        # Real
        unknown_real_accs = TradingAccount.objects.non_demo().filter(is_deleted=False)\
            .exclude(mt4_pk__in=list(RealUser.objects.values_list('login', flat=True)))
        archived_real_accs = ArchiveUser.objects\
            .filter(login__in=list(unknown_real_accs.values_list('mt4_id', flat=True)))
        TradingAccount.objects.filter(mt4_pk__in=list(archived_real_accs.values_list('login', flat=True)))\
            .update(is_deleted=True, is_archived=True)

        # Demo
        TradingAccount.objects.demo().filter(is_deleted=False)\
            .exclude(mt4_pk__in=list(DemoUser.objects.values_list('login', flat=True)))\
            .update(is_deleted=True,
                    deleted_comment="<Is a DEMO account. Automatically deleted by archivation.>")