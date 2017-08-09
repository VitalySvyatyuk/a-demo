# -*- coding: utf-8 -*-
import collections
from datetime import timedelta, date

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.db.models import Count
from django.template.loader import render_to_string

from crm.assignment_logic import get_base_clients_qs
from crm.models import PersonalManager
from crm.utils import prev_workday_since
from geobase.models import Country


def send_report(to, date_from, date_to, managers=None):
    if not isinstance(to, collections.Iterable):
        to = [to]

    managers = list(set(list(managers or []) + list(to)))

    stats = PersonalManager.manager_stats([m.user for m in managers], date_from, date_to)
    stats.sort(key=lambda s: s['manager'].crm_manager.office.pk if s['manager'].crm_manager.office else None)  # for template groupby

    lang_slug_to_display = dict(Country.LANGUAGES)
    new_users = sorted([
        (lang_slug_to_display.get(lang), count)
        for lang, count in User.objects.filter(
            date_joined__gte=date_from,
            date_joined__lt=date_to
        ).values_list('profile__country__language').annotate(count=Count('id'))
    ], key=lambda d: d[1], reverse=True)

    new_users_country = User.objects.filter(
        date_joined__gte=date_from,
        date_joined__lt=date_to
    ).values_list('profile__country__name_ru').annotate(count=Count('id')).order_by('-count')

    current_free = sorted([
        (lang_slug_to_display.get(lang), count)
        for lang, count in get_base_clients_qs().values_list('profile__country__language').annotate(count=Count('id'))
    ], key=lambda d: d[1], reverse=True)
    context = {
        'date_from': date_from,
        'date_to': date_to - timedelta(1),  # -1 day to make it pretty
        'managers': stats,
        'new_users_count': sum([count for lang, count in new_users], 0),
        'new_users_by_lang_count': new_users,
        'new_users_by_country_count': new_users_country,
        'current_free_count': sum([count for lang, count in current_free], 0),
        'current_free_by_lang_count': current_free,
        'current_rotten': {
            'count': User.objects.filter(
                profile__manager__is_active=False).count(),
            'managers': [u.get_full_name() for u in User.objects.filter(
                is_active=False
            ).annotate(
                clients_count=Count('managed_profiles')
            ).filter(
                clients_count__gt=0
            )]
        },
        'to': to,
    }
    html_content = render_to_string('gcrm/emails/managers_summary_report.html', context)

    recipients = tuple(m.user.email for m in to)
    send_mail(
        u'Отчёт по работе менеджеров за {} - {}'.format(date_from, date_to - timedelta(1)),
        message='-',
        html_message=html_content,
        from_email="security@grandcapital.net",
        recipient_list=recipients)


class Command(BaseCommand):
    args = 'date_at'
    # RECEPIENTS = (
    #     'd.tomilin@grandcapital.net',
    #     'solovyov@grandcapital.net')

    def handle(self, date_at, *args, **options):
        if date_at == 'since_last_workday':
            date_from = prev_workday_since()
            date_to = date.today()

        elif date_at == 'yesterday':
            date_from = date.today() - timedelta(1)
            date_to = date.today()

        elif date_at == 'prev_month':
            today = date.today()
            date_to = today.replace(day=1)
            date_from = (date_to - timedelta(1)).replace(day=1)

        elif date_at == 'today':
            date_from = date.today()
            date_to = date.today() + timedelta(1)

        sent_reports = []
        base_managers = PersonalManager.objects.active().our_office_or_local()

        # total managers report
        whoa = PersonalManager.objects.filter(user__pk__in=[
            58, 37479, 140743  # s.kozlovsky and e.solovyova and DTom and tamaz t.volchetckiy
        ])
        send_report(whoa, date_from, date_to, managers=base_managers)
        sent_reports += [37479]

        # partnership managers
        # aglezeris = PersonalManager.objects.get(user__pk=87328)
        # send_report(aglezeris, date_from, date_to, managers=base_managers.partnership())
        # sent_reports.append(87328)

        # offices head managers
        for man in base_managers.filter(is_office_supermanager=True).exclude(office=None):
            send_report(man, date_from, date_to, base_managers.filter(office=man.office))
            sent_reports.append(man.user.pk)

        # each other manager should get personal report
        for man in base_managers:
            if man.user.pk not in sent_reports:
                send_report(man, date_from, date_to)
