# -*- coding: utf-8 -*-
import cPickle
import re
from _mysql import OperationalError
from datetime import datetime, timedelta
from sys import getsizeof

import pytz
from annoying.decorators import render_to, ajax_request
from celery.app import default_app
from celery.result import BaseAsyncResult
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import DatabaseError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.context import RequestContext
from django.template.loader import get_template, TemplateDoesNotExist, render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from djcelery.backends.cache import CacheBackend

from notification import models as notification
from currencies import currencies
from issuetracker.models import RestoreFromArchiveIssue, ApproveOpenECNIssue
from log.models import Logger, Events
from otp.views import security_check, security
from platforms.converter import convert_currency
from platforms.forms import ChangeLeverageForm, PasswordRecoveryForm
from platforms.models import TradingAccount
from platforms.mt4.external.models_other import Mt4Quote
from platforms.types import get_account_type
from project.views import LoginRequiredMixin, AjaxFormView
from shared.decorators import as_json
from shared.forms import AccountChooseForm

from logging import getLogger
log = getLogger(__name__)


@login_required
@render_to("agent_list.html")
def agent_list(request, account_id=None):
    if "account_id" in request.POST:
        return redirect("mt4_agent_list", request.POST["account_id"])

    if account_id:
        try:
            account_id = int(account_id)
        except:
            raise Http404
        if not request.user.is_superuser:
            account = get_object_or_404(TradingAccount, user=request.user,
                                        mt4_id=account_id,
                                        is_deleted=False)
        else:
            # HACK: "group_name" is set, cause if it is not, the model
            # will be saved, which will cause an IntegrityError
            account = TradingAccount(mt4_id=account_id, group_name='real_ib')
    else:
        accounts = request.user.accounts.active().real_ib()
        if not accounts:
            raise Http404
        elif len(accounts) > 1:
            return {"form": AccountChooseForm(accounts),
                    "TEMPLATE": "agent_list_choose.html"}
        else:
            account = accounts[0]

    try:
        res = {}
        for agent_type in ["agents", "demo_agents"]:
            res[agent_type] = []
            for mt4_user in getattr(account, agent_type):
                acc_type = get_account_type(mt4_user.group)
                mt4_acc = TradingAccount.objects.filter(mt4_id=mt4_user.login)

                res[agent_type].append({
                    "group": acc_type,
                    "mt4": mt4_user,
                    "site": None if not mt4_acc else mt4_acc[0]
                })

    except (OperationalError, DatabaseError):
        return HttpResponse("This operation is currently unavailable")

    return {
        "agents": res["agents"],
        "demoagents": res["demo_agents"],
        "account": account
    }


@login_required
@render_to("verify_docs.html")
def verify_docs(request):
    user_verified = request.user.profile.status == request.user.profile.VERIFIED
    if not ApproveOpenECNIssue.objects.filter(author=request.user).exists() and user_verified:
        notification.send([request.user], 'apllication_for_invest_created')
        ApproveOpenECNIssue.objects.create(author=request.user)

    return {'user_verified': user_verified,
            'user_allow_open_invest': request.user.profile.allow_open_invest
            }


@login_required
@render_to("create_account.html")
def create_account(request, slug, extra_context=None):
    account_type = get_account_type(slug)
    if not account_type:
        raise Http404()

    if account_type.login_required and request.user.is_anonymous():
        return redirect(settings.LOGIN_URL + "?next=%s" % request.path)

    if not (account_type.is_demo or request.user.profile.has_otp_devices):
        messages.info(request, _("You need to set up a secure authentication method before opening a Real account."))
        return redirect(reverse("otp_security") + "?next=" + request.path)

    num_of_accounts = CreateAccountView.max_accounts_reached(request.user, account_type)
    if num_of_accounts:
        return {
            'documents_unverified': False,
            "too_many_accounts": True,
            "num_of_accounts": num_of_accounts,
            "acc_type": account_type
        }

    if request.POST:
        form = account_type.account_form(request.POST, request.FILES, request=request)
        if form.is_valid():
            form_result = form.save(profile=request.user.profile)

            if form.save.async:
                return redirect("mt4_wait_for_account_creation", form_result)
            else:

                if isinstance(form_result, HttpResponse):
                    return form_result

                Logger(user=request.user, content_object=form_result,
                       ip=request.META["REMOTE_ADDR"], event=Events.ACCOUNT_CREATED).save()

                kwargs = {
                    "slug": account_type.slug,
                    "account_id": form_result.mt4_id
                }

                done_url = reverse('mt4_account_welcome', kwargs=kwargs)
                if request.GET.get('next'):
                    return redirect(done_url + '?next=%s' % request.GET.get('next'))
                else:
                    return redirect(done_url)
    else:
        form = account_type.account_form(request=request)

    result = {"forms": {"account": form}}
    if extra_context is not None:
        result.update(extra_context)
    return result


def convert_balances(accounts, to_currency):
    results = {}

    for acc_id, acc in accounts.iteritems():
        if acc["balance"] is None:
            continue
        elif to_currency is None:
            b, c = acc["balance"], acc["currency"]
        else:
            b, c = convert_currency(acc["balance"], acc["currency"], to_currency)

        results[acc_id] = {
            "balance": c.display_amount(b, with_slug=c.slug) if b is not None else "",
            "currency": c.slug
        }

    return results


@as_json
@require_GET
@login_required
def balance(request):
    """
    Returns balance for a given account in the requested currency,
    which defaults to USD, unless no_default_currency is set
    """
    only_digits = re.compile("^[0-9]+$")
    accounts = map(int, [x for x in request.GET.getlist("accounts[]") if only_digits.match(x)])

    currency = currencies.get_currency(request.GET.get("currency", "USD"))

    accounts = TradingAccount.objects.filter(mt4_pk__in=accounts, user=request.user).order_by("mt4_id")

    if accounts:
        accounts = {account.mt4_id: {"balance": account.balance_money.amount,
                                     "currency": account.currency} for account in accounts}
    else:
        accounts = None

    return convert_balances(accounts, currency) if accounts else None


@login_required
@render_to("account_history.html")
def account_history(request, account_id):
    log.debug("Rendering account history for account {}".format(account_id))
    crm_staff = request.user.is_superuser
    log.debug("User is super: {}".format(crm_staff))

    # Managers should be able to see all the history for all the accounts
    if crm_staff:
        accounts = TradingAccount.objects.filter(mt4_id=account_id)
    else:
        accounts = TradingAccount.objects.filter(mt4_id=account_id, user=request.user, is_deleted=False)

    #one account can belong to multiple users - so there will be multiple mt4accounts
    #we should take first one
    if not accounts:
        raise Http404
    account = accounts[0]
    log.debug("Found account: {}".format(account))

    cache_key = "history.%i" % int(account_id)
    start = None
    history = account.get_history(start=start, opened=False, count_limit=200)
    log.debug("History length: {}".format(len(history)))

    if not history:
        log.warn("History not found, trying cache!")
        history_pickled = cache.get(cache_key, None)
        history = cPickle.loads(history_pickled) if history_pickled else []
        messages.error(request, _("Error while loading account data. Using cached data."))
    else:
        log.debug("History found, updating cache")
        history_pickled = cPickle.dumps(history)
        if getsizeof(history_pickled) < 1024 ** 2:  # If size is smaller than 1 MiB
            cache.set(cache_key, history_pickled)

    # TODO calculate
    total_profit = "---"

    open_operations_date = datetime(1970, 1, 1, tzinfo=pytz.utc)

    result = {
        "account": account,
        "history": history,
        "open_operations_date": open_operations_date,
        'total_profit': total_profit,
        'crm_staff': crm_staff,
    }

    if crm_staff:
        result.update({
            "TEMPLATE": "crm/account_history.html",
            'open_operations_profit': 0,

        })
    log.debug("Final result is: {}".format(result))
    return result


@ensure_csrf_cookie
@render_to("wait_for_account_creation_ajax.html")
def wait_for_account_creation(request, task_id):
    return {"task_id": task_id}


@render_to()
def welcome_account(request, account_id, user_id=None, slug=None):
    """Welcome screen, displayed when new account is created."""
    if user_id is not None:
        account = get_object_or_404(TradingAccount,
                                    mt4_id=account_id, user=user_id,
                                    is_deleted=False)
    elif request.user.is_authenticated():
        account = get_object_or_404(TradingAccount,
                                    mt4_id=account_id, user=request.user,
                                    is_deleted=False)
    else:
        raise Http404

    # Checking if we have a custom welcome template for acount's
    # group, if not — falling back to base.html.
    try:
        template = "mt4/welcome/%s.html" % (slug or account.group.slug)
        get_template(template)
    except TemplateDoesNotExist:
        template = "mt4/welcome/base.html"
    finally:
        return {"TEMPLATE": template,
                "account_type": get_account_type(slug) or account.group,
                "account": account,
                "group_slug": slug or account.group.slug,
                "next": request.GET.get('next')}


@login_required
@render_to("password_recovery.html")
def password_recovery(request, account_id):
    account = get_object_or_404(TradingAccount,
                                mt4_id=account_id, user=request.user,
                                is_deleted=False)
    form = PasswordRecoveryForm(data=request.POST or None)
    if form.is_valid():

        if not account.is_demo:
            result = security_check(request, request.user)
            if result:
                return result

        form.save(account=account)

        Logger(user=request.user, content_object=account,
               ip=request.META["REMOTE_ADDR"], event=Events.ACCOUNT_PASSWORD_RESTORED).save()

        messages.success(request,
                         _("Password recovery request for account #%(id)s "
                           "created successfully. Notification with the account "
                           "password has been sent to your e-mail.") % \
                         {"id": account.mt4_id})
        return redirect("mt4_account_list")

    return {"form": form}


@login_required
@render_to("change_leverage.html")
def change_leverage(request, account_id):
    account = get_object_or_404(TradingAccount,
                                mt4_id=account_id, user=request.user,
                                is_deleted=False)

    max_leverage = request.GET.get("max_leverage")

    if request.GET.get("next") == reverse("bonus_list"):
        max_leverage = 100

    form = ChangeLeverageForm(request.POST or None, account=account, max_leverage=max_leverage)
    if form.is_valid():

        if not account.is_demo:
            result = security_check(request, request.user)
            if result:
                return result

        form.save()

        Logger(user=request.user, content_object=account,
               ip=request.META["REMOTE_ADDR"], event=Events.LEVERAGE_CHANGED,
               params={"from": account.leverage, "to": form.cleaned_data["leverage"]}).save()

        messages.success(request,
                         _("Leverage for account #%(id)s changed successfully.") % {"id": account.mt4_id})
        return redirect(request.GET.get("next", "mt4_account_list"))

    return {"form": form}


@login_required
def restore_from_archive(request, account_id):
    account = get_object_or_404(TradingAccount,
                                mt4_id=account_id, user=request.user,
                                is_deleted=True, is_archived=True)
    issue = RestoreFromArchiveIssue(account=account)
    issue.save()
    messages.success(request,
                     _("Request #%(id)s created successfully.") % \
                     {"id": issue.pk})
    return redirect("mt4_account_list")


@ajax_request
def ajax_account_creation_done(request, task_id):
    result = BaseAsyncResult(task_id, CacheBackend(default_app))

    if not result.ready():
        return {
            "ok": True,
            "ready": False
        }

    result = result.get()

    return {
        "ok": True,
        "ready": True,
        "slug": result['slug'],
        "mt4_id": result['mt4_id'],
        "mt4_password": result['mt4_password'],
        "redirect": reverse("mt4_account_welcome", args=[result['slug'], result['mt4_id']]),
    }


@ajax_request
def get_account_welcome_page(request):

    account_type = get_account_type(request.GET["slug"])
    account = TradingAccount.objects.filter(mt4_id=request.GET["mt4_id"])[0]

    return {
        "welcome_page": render_to_string(
            ["mt4/welcome/%s.html" % account_type.slug, "mt4/welcome/base.html"],
            RequestContext(request, {
                "account_type": account_type,
                "account": account,
                "alternate_base": "ajax_base.html",
            })
        )
    }


@login_required
@render_to('account_list.html')
def account_list(request):
    accounts = request.user.accounts.active().order_by("mt4_id")
    try:
        h = int(request.GET.get("highlight"))
    except (ValueError, TypeError):
        h = None
    return {
        'accounts': accounts,
        'highlight': h,
    }


@cache_page(10)
@ajax_request
def quotes_info(request):
    """
    Returns quotes for symbols in QUOTES_FROM_MT4 in JSON
    """
    quotes_list = {
        #'$SPX': 'S&P500', # Until S&P500 returned to specs database (by request of Vinogradov)
        'EURUSD': 'EUR/USD',
        'GBPUSD': 'GBP/USD',
        'GOLD': 'GOLD',
        'USDCHF': 'USD/CHF',
        'USDJPY': 'USD/JPY',
        'USDRUR': 'USD/RUR'
    }

    result = list(
        Mt4Quote.objects.filter(symbol__in=quotes_list.keys())
                        .values("symbol", "direction", "ask", "bid", "high", "low")
    )

    if not result:
        return {}  # in JS we need a dict, even if we got nothing to return

    # Update symbols to show
    for row in result:
        row.update(symbol=quotes_list[row['symbol']])

    return {
        'quotes': result
    }


@login_required
@ajax_request
def account_info(request, acc_id=None):
    full_view = False
    if acc_id is None:
        accounts = request.user.accounts.all()
    else:
        if request.user.has_perm("payments.can_add_transactions"):
            full_view = True
        elif not request.user.accounts.filter(mt4_id=acc_id).exists():
            raise Http404

        accounts = TradingAccount.objects.filter(mt4_id=acc_id)

    res = {"accounts": {}}
    for acc in accounts:

        balance = acc.get_balance(with_bonus=True)[0]
        leverage = acc.leverage

        details = acc.get_bonus_details()

        res["accounts"][acc.mt4_id] = {
            "account": unicode(acc),
            "balance": acc.currency.display_amount(balance) if balance is not None else "",
            "leverage": acc.leverage if leverage else "",
        }

        if full_view:
            res["accounts"][acc.mt4_id]["bonuses"] = ([(bonus_name, acc.currency.display_amount(amount))
                                                       for bonus_name, (amount, _) in
                                                       details.items()]
                                                      if details else None)
            res["accounts"][acc.mt4_id]["currency"] = acc.currency.slug
        else:
            res["accounts"][acc.mt4_id]["bonuses"] = (acc.currency.display_amount(sum(amount
                                                                                      for amount, currency in
                                                                                      details.values()
                                                                                      if amount > 0))
                                                      if details else None)

    return res


class CreateAccountModalView(LoginRequiredMixin, AjaxFormView):

    def get(self, request):
        if request.is_ajax():
            return self.json_response({
                "ok": True,
                "simple_redirect": request.path,
            })
        # just give plain page
        return render_to_response("private_office/static_pages/create_account.html",
                                  RequestContext(request, {}))


class CreateAccountView(LoginRequiredMixin, AjaxFormView):
    @staticmethod
    def max_accounts_reached(user, account_type):
        # We will count deleted accounts, but won't count archived
        num_of_accounts = user.accounts.by_groups(account_type).active().count()
        if num_of_accounts < account_type.max_per_user:
            return False
        return num_of_accounts

    def get(self, request, slug):
        # get form
        template = "includes/create_account_form_with_errors.html"
        account_type = get_account_type(slug)

        if str(account_type) == 'ECN.Invest' and not request.user.profile.allow_open_invest:
            return redirect('verify_docs')

        if not account_type.is_demo and request.user.profile.status == request.user.profile.UNVERIFIED:
            # return self.json_response({
            #     "redirect": redirect("mt4_create_account", slug=21)
            # })
            return redirect("verify_docs")

        if not account_type.is_demo and request.user.profile.status < request.user.profile.UNVERIFIED:
            return redirect("account_app")

        if not (account_type.is_demo or request.user.profile.has_otp_devices):
            return security(request)

        if not request.is_ajax():
            return redirect("mt4_create_account", slug)

        num_of_accounts = self.max_accounts_reached(request.user, account_type)
        if num_of_accounts:
            return render_to_response(
                template,
                RequestContext(request,
                               {"too_many_accounts": True, "num_of_accounts": num_of_accounts, "acc_type": account_type})
            )

        form = account_type.account_form(request=request, account_type=account_type)

        return render_to_response(template,
                                  RequestContext(request, {"form": form, "acc_type": account_type}))

    def post(self, request, slug):
        # post form

        account_type = get_account_type(slug or request.POST.get("account_type"))

        if not account_type.is_demo and request.user.profile.status == request.user.profile.UNVERIFIED:
            return self.json_response({
                "redirect": redirect("verify_docs")
            })

        if not account_type.is_demo and request.user.profile.status < request.user.profile.UNVERIFIED:
            return self.json_response({
                "redirect": redirect("account_app")
            })

        if self.max_accounts_reached(request.user, account_type):
            return self.json_response({
                "redirect": redirect("mt4_create_account", args=[slug])
            })
        assert 'OK'
        if not (account_type.is_demo or request.user.profile.has_otp_devices):
            return security(request)

        form = account_type.account_form(request.POST, request=request, account_type=account_type)

        if form.is_valid():
            form_result = form.save(profile=request.user.profile)

            if getattr(form.save, 'async', None):
                return self.json_response({
                    "ok": True,
                    "wait": reverse("mt4_ajax_account_creation_done", args=[form_result]),
                })

            account = form_result['account']

            Logger(user=request.user, content_object=account,
                   ip=request.META["REMOTE_ADDR"], event=Events.ACCOUNT_CREATED).save()

            return self.json_response({
                "ok": True,
                "no_wait": True,
                "slug": account_type.slug,
                "mt4_id": account.mt4_id,
                "mt4_password": form_result["password"],
                "platform": account.platform_type,
                "login": account._login,
                "redirect": reverse("mt4_account_welcome", args=[account_type.slug, account.mt4_id]),
            })

        return self.json_response({
            "nok": True,
            "errors": {k: map(unicode, v) for k, v in form.errors.items()},
        })


@login_required
@ajax_request
def get_ib_accounts(request):

    ib_accounts = request.user.accounts.alive().real_ib().values("id", "mt4_id")

    return {
        "accounts": list(ib_accounts)
    }
