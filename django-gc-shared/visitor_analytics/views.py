# coding=utf-8
from django.contrib.auth.decorators import permission_required

from annoying.decorators import render_to

from platforms.converter import convert_currency
from platforms.mt4.models import TradingAccount

from payments.models import DepositRequest

from visitor_analytics.forms import UtmReportForm
from visitor_analytics.models import UtmAnalytics


@permission_required('visitor_analytics.can_view_utm_report')
@render_to('visitor_analytics/report.html')
def utm_report(request):
    if request.POST:
        form = UtmReportForm(request.POST)
        if form.is_valid():
            utms = UtmAnalytics.objects.all()
            if form.cleaned_data['utm_source']:
                utms = utms.filter(utm_source__in=form.cleaned_data['utm_source'])
            if form.cleaned_data['utm_medium']:
                utms = utms.filter(utm_medium__in=form.cleaned_data['utm_medium'])
            if form.cleaned_data['utm_campaign']:
                utms = utms.filter(utm_campaign__in=form.cleaned_data['utm_campaign'])
            user_count = utms.filter(
                user__date_joined__gte=form.cleaned_data['date_from'],
                user__date_joined__lte=form.cleaned_data['date_to'],
            ).count()
            mt4_accounts = TradingAccount.objects.filter(
                user__utm_analytics__in=utms,
                creation_ts__gte=form.cleaned_data['date_from'],
                creation_ts__lte=form.cleaned_data['date_to'],
            )
            groups_accounts = {}
            # Okay, that seems like a slow code, but we don't have any better means to reliably determine group
            for mt4_acc in mt4_accounts:
                groups_accounts.setdefault(mt4_acc.group, []).append(mt4_acc)
            groups_count = {group: len(accounts) for group, accounts in groups_accounts.iteritems()}
            groups_deposit = {}
            for group, accs in groups_accounts.iteritems():
                deposits = DepositRequest.objects.filter(
                    is_committed=True,
                    is_payed=True,
                    account__pk__in=map(lambda x: x.pk, accs),
                )
                sum_usd = 0
                for deposit in deposits:
                    sum_usd += convert_currency(deposit.amount, from_currency=deposit.currency,
                                                to_currency='USD', for_date=form.cleaned_data['date_from'])[0]
                groups_deposit[group] = sum_usd

            groups = sorted(groups_count.keys())
                
            return {'form': form,
                    'should_show_form': True,
                    'report': {
                        'data': {
                            'groups': groups,
                            'user_count': user_count,
                            'groups_count': (groups_count[group] for group in groups),
                            'groups_deposit': (groups_deposit[group] for group in groups),
                        }
                    }}

    else:
        form = UtmReportForm()

    return {'form': form, 'should_show_form': True}
