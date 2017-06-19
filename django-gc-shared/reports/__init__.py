# coding=utf-8
default_app_config = 'reports.apps.ReportsConfig'

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_migrate

from annoying.decorators import signals
from shared.utils import define

from reports import models as reports

# Report types
SINGLE_ACCOUNT = 0
PRIVATE_OFFICE = 1
ACCOUNT_GROUP = 2
GLOBAL = 3


# список всех возможных отчетов, где:
# ключ = используется при проверке разрешений вида `can_generate_%(report)`,
# name = полное название отчета,
# default = флаг доступности отчета свежесозданным пользователям (True = доступен),
# account_group_filter = флаг использования групп влючить/исключить для отчета (True = использует)
define("REPORTS", {
    ########################## отчет, доступный по умолчанию
    "closed_trades": {
        "name": _("Closed trade report"),
        "default": True,
        "type": SINGLE_ACCOUNT,
    },
    ##########################
    ########################## отчеты, не требующие указания аккаунта при оформлении
    # No reports for now
    ########################## отчёты, не требующие указания счёта, собирающиеся по данным ЛК
    ########################## текущего пользователя
    # No reports for now
    ##########################
    ########################## отчеты, требующие указания аккаунта при оформлении
    "summary": {
        "name": _("Summary report"),
        "default": False,
        "type": SINGLE_ACCOUNT,
    },
    ##########################
    ########################## групповые отчеты
    # No reports for now
    ##########################
})


@receiver(post_migrate)
def create_permissions(sender, **kwargs):
    if sender.label != 'reports':
        return

    for codename in settings.REPORTS:
        permission, created = Permission.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(reports.Report),
            codename="can_generate_%s" % codename)

        if created:
            permission.name = "Can generate %s" % settings.REPORTS[codename]["name"].lower()
            permission.save()
            print "Adding permission: %s" % permission

    permission, created = Permission.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(reports.Report),
        codename="can_use_any_account")

    if created:
        permission.name = "Can generate reports for all accounts"
        permission.save()
        print "Adding permission: %s" % permission

    permission, created = Permission.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(reports.Report),
        codename="can_use_account_groups")

    if created:
        permission.name = "Can generate reports for account groups"
        permission.save()
        print "Adding permission: %s" % permission

    permission, created = Permission.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(reports.Report),
        codename="can_use_any_user")

    if created:
        permission.name = "Can generate reports for other users"
        permission.save()
        print "Adding permission: %s" % permission

    Permission.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(reports.Report),
        codename="can_use_excel",
        defaults={'name': "Can access Excel export"})


@signals.post_save(sender=User)
def create_default_permissions(sender, instance, **kwargs):
    for codename in settings.REPORTS:
        if not settings.REPORTS[codename]["default"] or \
           instance.has_perm("reports.can_generate_%s" % codename):
            continue

        if Permission.objects.filter(codename="can_generate_%s" % codename).exists():
            instance.user_permissions.add(
                Permission.objects.get(codename="can_generate_%s" % codename)
            )
