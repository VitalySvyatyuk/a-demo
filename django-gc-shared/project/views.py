# -*- coding: utf-8 -*-

import json
import logging

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import settings
import math

from collections import OrderedDict
from itertools import chain
from annoying.decorators import render_to
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View
from django.utils.translation import ugettext_lazy as _, get_language

from platforms.mt4.external.models_other import Mt4Quote, Mt4OpenPrice
from platforms.models import ChangeQuote
from geobase.utils import get_geo_data
from uptrader_cms.models import CompanyNews

from payments.models import PaymentMethod
from project.utils import maybe_ajax
from massmail.models import MailingList, Subscribed
from django.views.decorators.csrf import csrf_exempt

log = logging.getLogger(__name__)


def render_template(request, category, name):
    return render(request, "js/{category}/{name}.html".format(category=category, name=name))


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)

        def inner(request, *args, **kwargs):
            if request.user.is_authenticated():
                return view(request, *args, **kwargs)
            from registration.views import register
            return register(request, next=request.path, *args, **kwargs)
        return inner


class AjaxFormView(View):
    def json_response(self, data, **response_kwargs):
        data = json.dumps(data)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)


@ensure_csrf_cookie
@render_to("js/my/my.html")
@login_required
def app_my(request):
    if request.user.profile.registered_from:
        logout(request)

    if not request.user.profile.country:
        geo_data = get_geo_data(request) if request else {}
        request.user.profile.country = geo_data.get("country")
        request.user.profile.state = geo_data.get("region")
        request.user.profile.save()

    if request.is_ajax():
        data = json.dumps({
            "ok": True,
            "simple_redirect": request.path,
        })
        return HttpResponse(data, content_type='application/json')

    if request.user.profile.lost_otp and '/account/profile/security' not in request.path:
        return redirect("/account/profile/security")

    new_registration = request.session.get("new_registration")
    from_facebook = 'false'
    if new_registration:
        del request.session["new_registration"]
        if hasattr(request.user, 'utm_analytics')\
                and 'facebook.com' in request.user.utm_analytics.referrer:
            from_facebook = "true"

    return {
        'new_registration': new_registration or 'false',
        'from_facebook': from_facebook,
        'company_news': CompanyNews.objects.published().filter(
            language=request.LANGUAGE_CODE
        )[:4]
    }


@ensure_csrf_cookie
@render_to("js/my/my_mobile.html")
@login_required
def mobile_app_my(request):
    if request.is_ajax():
        data = json.dumps({
            "ok": True,
            "simple_redirect": request.path,
        })
        return HttpResponse(data, content_type='application/json')
    return {}


@render_to("js/my/my.html")
@login_required()
def private_offices(request, slug):
    if request.user.profile.registered_from != slug:
        logout(request)

    if request.is_ajax():
        data = json.dumps({
            "ok": True,
            "simple_redirect": request.path,
        })
        return HttpResponse(data, content_type='application/json')
    if settings.PRIVATE_OFFICES:
        private_office_settings = settings.PRIVATE_OFFICES.get(slug, {})
    else:
        private_office_settings = {}

    cfg = {
        'config': {
            'css': private_office_settings['css'],
            'url': '/private_office/{}/'.format(slug),
            'available_accounts': private_office_settings['available_accounts'],
            'available_modules': private_office_settings['available_modules']
        }
    }

    return cfg


# @render_to('marketing_site/pages/index.jade')
def frontpage(request):
    # QUOTES NEEDED LOOKS LIKE:
    # quotes_needed = OrderedDict(
    #     ((_('Currencies'), ('EURUSD', 'GBPUSD', 'AUDCAD', 'NZDUSD', 'EURJPY', 'EURCHF', 'USDRUB', 'USDCNY')),
    #      (_('Metals'), ('GC', 'HG', 'PA', 'PL', 'SI', 'CT', 'ES', 'DX')),
    #      (_('Indices'), ('FDAX', 'AEX', 'DX', 'ES', 'FCE', 'FTSE', 'YM', 'NQ')))
    # )

    show_language_choice_modal = request.GET.get('show')
    if show_language_choice_modal and show_language_choice_modal.lower() != "true":
        show_language_choice_modal = False
    else:
        show_language_choice_modal = True


    quotes_needed = OrderedDict()

    for quotes_tab_needed in ChangeQuote.objects.all():
        quotes_needed[_(quotes_tab_needed.category)] = quotes_tab_needed.quotes.replace(' ', '').split(',')
    result = OrderedDict()
    try:
        symbols_list = list(chain(*quotes_needed.values()))

        quotes = list(
            Mt4Quote.objects.filter(symbol__in=symbols_list)
                .values('symbol', 'bid', 'ask', 'spread', 'direction', 'digits')
        )

        for key, pairs in quotes_needed.items():
            result[key] = []

            for pair in pairs:
                try:
                    quote = filter(lambda x: x["symbol"] == pair, quotes)
                    if not quote:
                        log.warn("Quote {} not found in MT4".format(pair))
                        continue
                    quote = quote[0]
                    tmp = dict(quote)

                    tmp["spread_digits"] = quote['digits']
                    # prob incorrect calculations
                    tmp["spread"] = "%.1f" % ((tmp["ask"] - tmp["bid"]) * (10 ** (quote['digits']-1)))
                    #tmp["percents"] = "%+.2f" % ((tmp["bid"] - tmp["open_price"]) / tmp["open_price"] * 100)
                    tmp["percents"] = "---"
                    result[key].append(tmp)
                except Exception as e:  # anything can happen here :(
                    log.warn(e)
                    continue
    except AttributeError as e:
        # too broad exception because MySQL exceptions are not proxied by Django's DatabaseError :(
        log.warn(e)

    context = {
        "company_news": CompanyNews.objects.published().filter(language=request.LANGUAGE_CODE)[:3],
        "quotes": result
    }

    response = render(request, 'marketing_site/pages/index.jade', context=context)
    if not show_language_choice_modal:
        response.set_cookie('show', 'false')

    return response


@render_to('marketing_site/pages/inout.jade')
def inout(request):
    conditions = PaymentMethod.objects.select_related('category').filter(
        languages__contains=[request.LANGUAGE_CODE]
    )
    return {
        "deposit_systems": (
            x for x in conditions if x.payment_type == PaymentMethod.DEPOSIT),
        "withdraw_systems": (
            x for x in conditions if x.payment_type == PaymentMethod.WITHDRAW)
    }


@maybe_ajax('marketing_site/pages/partnership.jade')
def partnership(request):

    from callback_request.models import CallbackRequest
    if request.method == 'POST':
        form = CallbackRequest(phone_number=request.POST.get('phone'),
                               email=request.POST.get('email'),
                               name=request.POST.get('first_name'),
                               internal_comment=u'User from site: {},\ncompany: {},\ncountry: {}\nwanna be official agent'
                               .format(request.POST.get('site'), request.POST.get('company'), request.POST.get('country'),)
                               )
        form.save()
        send_mail(
            u"Application for becoming official agent",
            u'User: {} from site: {},\ncompany: {},\ncountry: {}\nwant to become official agent\nEmail: {}\nPhone: {}'.
                format(request.POST.get('first_name'), request.POST.get('site'),
                       request.POST.get('company'), request.POST.get('country'),
                       request.POST.get('email'), request.POST.get('phone')),
            settings.SERVER_EMAIL,
            settings.MANAGERS[0]  # Which means support email
        )
        return {'result': 'OK'}
    return {'request': request}

@csrf_exempt
@maybe_ajax()
def send_subscribe_email(request):

    from massmail.utils import get_signature
    from massmail.models import MailingList
    from project.utils import get_current_domain

    FOR_INVESTOR_MAIL_LIST_ID = (u"Руководство успешного инвестора", u"Руководство успешного инвестора (EN)")
    FOR_TRADER_MAIL_LIST_ID = (u"Руководство успешного трейдера", u"Руководство успешного трейдера (EN)")
    EDUCATION_MAIL_LIST_ID = (u"Учебный центр", u"Учебный центр (EN)")
    EVERYDAY_ANALYTICS_MAIL_LIST_ID = (u"Ежедневная аналитика", u"Ежедневная аналитика (EN)")

    if request.method == "POST":

        mail_list_id = [request.POST.get("id")] if request.POST.get("id") else []
        subscribe_form_checkbox = request.POST.getlist("subscribe-form-checkbox") or \
                                  [request.POST.get("subscribe-form-checkbox")]
        first_name = request.POST.get("first_name", "").replace(" ", "")
        last_name = request.POST.get("last_name", "").replace(" ", "")
        phone = request.POST.get("phone", "").replace(" ", "")

        if not mail_list_id:
            # trying to parse index page case
            if u"investor" in subscribe_form_checkbox:
                mail_list_id.append(FOR_INVESTOR_MAIL_LIST_ID[0 if get_language() == "ru" else 1])
            if u"trader" in subscribe_form_checkbox:
                mail_list_id.append(FOR_TRADER_MAIL_LIST_ID[0 if get_language() == "ru" else 1])
            # trying to parse education page
            if u"education" in subscribe_form_checkbox:
                mail_list_id.append(EDUCATION_MAIL_LIST_ID[0 if get_language() == "ru" else 1])
            # trying to parse pop-up
            if u"analytics" in subscribe_form_checkbox:
                mail_list_id.append(EVERYDAY_ANALYTICS_MAIL_LIST_ID[0 if get_language() == "ru" else 1])

        email = request.POST.get("email")
        domain = get_current_domain()
        mail_ids = []

        if not email or not mail_list_id:
            return {'result': 'NO'}
        else:
            signature = get_signature(email)
            email_subj = _("Confirm subscriptions to articles")
            for mail_id in mail_list_id:

                # since we decide search by mail_list_name
                try:
                    mail_ids.append(unicode(MailingList.objects.get(name=mail_id).pk))
                except (ObjectDoesNotExist, MultipleObjectsReturned):
                    log.error("Cant subscribe user for mail list with name: {}".format(request.POST.get("id")))
                    return {'result': 'NO'}

            mail_id = '+'.join(mail_ids)

            link = domain + reverse("massmail_subscribe_id", args=(signature, email, mail_id, first_name, last_name, phone))
            email_body = _("Hello! In order to confirm your email, please click here") + "\n" + link
            send_mail(
                email_subj,
                email_body,
                settings.SERVER_EMAIL,
                [email]
            )
        return {'result': 'OK'}


# def subscribewix(request):
#     if request.method == "POST":
#         ml = MailingList.objects.get(pk=20)
#         data = request.POST
#         sub = Subscribed(email=data.get("email", ""),
#                          first_name=data.get("first_name", ""),
#                          last_name=data.get("last_name", ""),
#                          phone=data.get("phone", ""))
#         ml.subscribers.add(sub)
#         ml.subscribers_count += 1
#         ml.save()
#     return
