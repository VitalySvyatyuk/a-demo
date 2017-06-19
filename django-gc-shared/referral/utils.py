# -*- coding: utf-8 -*-

from datetime import datetime, date
from functools import wraps

from django.http import HttpResponseForbidden, HttpResponseBadRequest

from referral.models import PartnerDomain, Click

NON_OVERWRITABLE_CODES = [125824, 108640]


def set_agent_code(request, agent_code, override_session=True, partner_domain_request=False):
    """Set the agent code for request

    If the user is authenticated, for profile.
    Else, for the session.
    """

    # (Igor) Due to a cyclic import bug, moved this import here
    # I was unable to fix it even after an hour of investigation
    from referral.models import Click

    click, created = Click.objects.get_or_create(agent_code=agent_code, date=date.today())
    if partner_domain_request:
        click.partner_domain_requests += 1
    else:
        click.clicks += 1
    click.save()

    if not request.user.is_authenticated():
        # http://crm.grandcapital.ru/view.php?id=1776
        if request.session.get('agent_code', None) in NON_OVERWRITABLE_CODES:
            return
        if 'agent_code' not in request.session or override_session:
            request.session['agent_code'] = agent_code
            request.session['agent_code_timestamp'] = datetime.now()


def get_clicks_for_user(user):
    clicks_list = [
        get_clicks_for_account(account.mt4_id)
        for account in user.accounts.real_ib().active()
    ]

    return {
        'clicks_list': clicks_list
    }


def get_clicks_for_account(mt4_id):

    clicks = [
        {
            'date': str(c.date),
            'clicks': c.clicks
        }
        for c in Click.objects.filter(agent_code=mt4_id).order_by('-date')[:100]
    ]
    return {
        'account': mt4_id,
        'clicks': clicks,
        'total': Click.objects.total(mt4_id)
    }
