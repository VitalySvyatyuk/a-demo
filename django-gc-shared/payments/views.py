# -*- coding: utf-8 -*-

import logging
import csv
import json
import base64

from datetime import datetime, date

from BeautifulSoup import BeautifulSoup

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, Http404, StreamingHttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from annoying.decorators import render_to, ajax_request

from log.models import Logger, Events
from currencies.currencies import get_currency
from currencies.money import Money
from platforms.exceptions import PlatformError
from platforms.converter import convert_currency
from payments.forms import (
    WithrawRequestFastDeclineForm, WithdrawRequestsGroupApprovalForm,
    AdditionalTransactionForm
)
from payments.models import DepositRequest, WithdrawRequest, WithdrawRequestsGroup, WithdrawRequestsGroupApproval
from payments.tasks import update_profit
from payments.utils import get_account_requests_stats
from requisits.models import UserRequisit

log = logging.getLogger(__name__)


@csrf_exempt  # LiqPay somehow sends the user back via POST request
def operation_status(request, operation, object_id=None, status=None):
    if request.user.is_anonymous():
        return HttpResponseForbidden()

    model = {"deposit": DepositRequest,
             "withdraw": WithdrawRequest}[operation]

    instance = get_object_or_404(
        model,
        # HACK: because Robokassa doesn't allow custom success / failure
        # urls, so we can't specify object_id via a URL string.
        pk=request.REQUEST.get("InvId", request.REQUEST.get("order_id", object_id))
    )

    if instance.payment_system == "wirecapital" and request.REQUEST.get('resultCode') == '0':
        status = 'fail'

    if status == "fail":
        instance.is_committed = False
        instance.is_payed = False
        instance.public_comment = _("Automatic payment failed.")
        instance.save()

    return redirect(reverse('account_app')+'messages')


@csrf_exempt
def operation_result(request, object_id=None):
    log.info("Processing incoming payment request from %s", request.META["REMOTE_ADDR"])
    log.debug("Request method: {}".format(request.method))
    log.debug("Request POST data: {}".format(request.POST))

    # HACK: because Robokassa, RBKMoney, mixplat, Yandex.Money and payeer don't allow custom result
    # urls, so we can't specify object_id via a URL string.
    object_id = (
        object_id or
        request.POST.get("InvId") or
        request.POST.get("m_orderid") or
        request.POST.get("merchant_order_id") or  # mixplat
        request.POST.get("orderId") or
        request.POST.get("tid") or
        request.POST.get("label") or
        request.POST.get("orderid") or
        request.POST.get("bill_id") or  # qiwi
        request.POST.get("MNT_TRANSACTION_ID") or  # moneta ru
        request.POST.get("orderRef", "grand_")[6:] or  # paymentasia
        request.POST.get("external_id") # accentpay
    )



    log.info("Payment object id is %s" % object_id)

    if not object_id:
        log.warn("Object id not found, looking for it in other places")
        if 'orderXML' in request.POST:  # CardPay
            data_xml = base64.b64decode(request.POST['orderXML'])
            soup = BeautifulSoup(data_xml)
            object_id = soup.order["number"]
        elif 'xml' in request.POST:  # PayBoutique
            soup = BeautifulSoup(request.POST['xml'])
            object_id = soup.message.orderid.text
        elif 'amount_readable' in request.body:  # OrangePay
            data = json.loads(request.body)
            object_id = data['data']['transaction']['reference_id']
        elif 'merchantTransactionId' in request.body:  # Naspay
            data = json.loads(request.body)['transaction']
            object_id = data['merchantTransactionId']
            # log.debug("Naspay Object Id: {}".format(object_id))
        else:
            return HttpResponseBadRequest()
        log.info("So now object id is {}".format(object_id))
    try:
        instance = DepositRequest.objects.get(pk=object_id)
    except DepositRequest.DoesNotExist:
        return Http404()

    log.info("Payment System is {}".format(instance.payment_system))
    try:
        form = instance.payment_system.get_form("deposit")
    except AttributeError:
        log.error("Payment System with no deposit form!")
        return HttpResponse(status=501) # Not implemented

    # noinspection PyBroadException
    try:
        verification_result = form.verify(request)
    except:  # Various errors can be expected here
        verification_result = False

    if not verification_result:
        log.error("Validation failed!")
        return HttpResponseBadRequest()

    log.info("Deposit Validation OK!")

    if not hasattr(form, "execute"):
        log.critical("execute() not implemented for %s method",
                     instance.payment_system)
        return HttpResponse(status=501)  # Not implemented.

    transaction_id = request.POST.get('transaction_id')


    if transaction_id is not None:
        log.info("transaction_id  is {}".format(transaction_id))
        instance.transaction_id = transaction_id

    log.info("Executing payment form")

    return form.execute(request, instance)

#TODO: Denis, refactoring
@login_required
@ajax_request
def request_data(request, operation):
    perm = 'payments.change_%srequest' % operation

    if operation == "withdraw":
        obj = get_object_or_404(WithdrawRequest, pk=request.GET.get('id'))
        ps = obj.payment_system
        req = obj.params
    else:
        obj = get_object_or_404(DepositRequest, pk=request.GET.get('id'))
        ps = obj.payment_system
        req = None

    amount = float(obj.amount)

    if operation == "deposit":
        calc = ps.DepositForm.calculate_commission
    elif operation == "withdraw":
        try:
            calc = ps.WithdrawForm.calculate_commission
        except AttributeError:
            # у платежной системы не определена комиссия
            from payments.systems.base import CommissionCalculationResult
            calc = lambda req: CommissionCalculationResult(
                amount=req.amount,
                commission=None,
                currency=req.currency
            )
    else:
        raise ImproperlyConfigured("Unknown operation type: {}".format(operation))

    if not request.user.has_perm(perm):
        return HttpResponseForbidden()

    if obj.conversion_rate:
        obj.converted_mt4_for_date_before = obj.creation_ts.strftime("%d.%m.%Y")
        obj.amount_converted_mt4_before = float(obj.amount) * obj.conversion_rate

    amount_now, curr, date_now = convert_currency(amount, obj.currency, obj.account.currency, return_date=True)

    obj.converted_mt4_for_date_now = date_now.strftime("%d.%m.%Y")
    obj.amount_converted_mt4_now = amount_now

    currency = get_currency(obj.currency)

    c = calc(obj)
    obj.commission = c.commission
    obj.commission_currency = c.currency
    # obj.amount это сумма уже с учетом комиссии
    # тогда, клиент получает obj.amount-obj.commission (если она есть)
    obj.what_client_gets = c.amount - (c.commission if c.commission is not None else 0)

    context = {'object': obj, "request": req, "operation": operation}
    try:
        context['balance'], context['balance_currency'] = obj.account.get_balance(currency)
    except AttributeError:
        pass

    context["is_ib"] = obj.account.is_ib
    context["stats"] = get_account_requests_stats(obj.account)

    params = obj.account.user.profile.params

    if "profit" in params and "profitability_deposit" in params:
        context["profit"] = params["profit"]
        context["profitability_deposit"] = params["profitability_deposit"]
        context["last_updated"] = datetime.strptime(params["last_updated"], "%Y-%m-%dT%H:%M:%S").strftime("%d.%m.%Y")

    context['is_visa'] = str(obj.payment_system) == 'Visa/Mastercard'

    if operation == "withdraw":
        update_profit(obj)

    return {
        'html': render_to_string('payments/request_data_ajax.haml', RequestContext(request, context)),
        'object': {
            'private_comment': obj.private_comment,
            'public_comment': obj.public_comment,
            'is_committed': obj.is_committed,
            'is_payed': obj.is_payed,
            'reason': obj.get_reason_display() if hasattr(obj, "get_reason_display") else None,
        }
    }


#TODO: Denis, refactoring
def _get_change_message(request, is_committed, is_payed):
    return (
        u"Changed comments via AJAX form. "
        u"Public comment: %s Private comment: %s "
        u"Is paid: %s Is committed: %s" % (
            request.POST.get('public_comment', '<no change>')
            if request.user.has_perm('payments.change_withdrawrequest')
            else "<no change>",
            request.POST.get('private_comment', '<no change>'),
            str(is_payed),
            str(is_committed)
        )
    )

#TODO: Denis, refactoring
@login_required
@ajax_request
@require_POST
def request_update(request, operation):
    '''
    This view updates withdraw/deposit requests from special admin form.
    '''
    from shared.utils import log_change

    change_perm = 'payments.change_%srequest' % operation

    if not request.user.has_perm(change_perm):
        return HttpResponseForbidden()

    if operation == "withdraw":
        obj = get_object_or_404(WithdrawRequest, pk=request.POST.get('request_id'))
        payed = {"false": False, "true": True, "": None}[request.POST["is_payed"]]
        committed = {"false": False, "true": True, "": None}[request.POST["is_committed"]]
    else:
        obj = get_object_or_404(DepositRequest, pk=request.POST.get('request_id'))

    # TODO: move this to a form for consistency
    is_committed = {'true': True, 'false': False}.get(request.POST.get('is_committed'), None)
    is_payed = {'true': True, 'false': False}.get(request.POST.get('is_payed'), None)

    if request.user.has_perm('payments.can_commit_payments'):
        obj.is_payed = is_payed
        obj.is_committed = is_committed
        obj.public_comment = request.POST.get('public_comment', '')

    obj.private_comment = request.POST.get('private_comment', '')

    try:
        obj.save()
    except PlatformError as e:
        if e.args and e.args[0] == e.NOT_ENOUGH_MONEY:
            return {
                "no_money": True,
            }

    log_change(request, obj, _get_change_message(request, is_committed, is_payed))

    return {}


#TODO: Denis, refactoring
@login_required
@staff_member_required
@render_to("payments/account_withdraw_requests_group.haml")
def account_withdraw_requests_group(request, group_id):
    """
    Codename AutoNoSick
    """
    group = get_object_or_404(WithdrawRequestsGroup, id=group_id)

    if 'user' in request.GET and (
            request.user.is_superuser or
            request.user.has_perm('payments.can_edit_approvals')):
        user = get_object_or_404(User, id=request.GET.get('user'))
    else:
        user = request.user
    approval, created = WithdrawRequestsGroupApproval.objects.get_or_create(group=group, user=user)
    form = WithdrawRequestsGroupApprovalForm(request.POST or None, instance=approval)

    if request.POST and form.is_valid():
        approval = form.save(commit=False)
        if 'is_accepted' in approval.changes:
            Logger(
                event=Events.WITHDRAW_REQUESTS_GROUP_APPROVAL_RESULT_CHANGED,
                user=request.user, ip=request.META["REMOTE_ADDR"],
                content_object=approval, params={'is_accepted': approval.is_accepted}).save()

        approval.updated_by = request.user
        approval.save()

        #set private comment in all available requiests
        if approval.comment:
            comment = u'{0}: {1}'.format(approval.user.get_full_name(), approval.comment)
            group.alive_requests.update(private_comment=comment)

    #recalculate all conditions and reprocess all with new conditions
    group.process()

    #create logs list
    logs = list()
    logs_for = lambda cls, ids: Logger.objects.filter(object_id__in=ids, content_type=ContentType.objects.get_for_model(cls))
    logs += logs_for(WithdrawRequestsGroup, [group.id])
    logs += logs_for(WithdrawRequest, group.requests.values_list('id', flat=True))
    logs += logs_for(UserRequisit, group.requests.values_list('requisit_id', flat=True))
    logs += logs_for(WithdrawRequestsGroupApproval, group.approvals.values_list('id', flat=True))

    logs.sort(key=lambda x: x.id, reverse=True)

    #for easy format
    if group.request_time_left:
        total_minutes = group.request_time_left.total_seconds() / 60.0
        hours, minutes = divmod(total_minutes, 60)
    else:
        hours, minutes = None, None

    not_payed = group.alive_requests.filter(is_payed=None)

    with Money.convert_cache_key('autonosick_converter_{0}'.format(date.today().strftime("%d/%m/%Y"))):
        # totals = group.account.get_totals()
        return {
            'active_balance_money': not_payed[0].active_balance_money if not_payed else _("No pending requests"),
            'all_requirements': sorted(group.all_requirements.items(), key=lambda x: x[1]['priority']),
            'current_level': group.next_required_level(),
            'current_balance': Money(*group.account.get_balance()),
            'approval': approval,
            'form': form,
            'group': group,
            'logs': logs,
            'all_requests': group.requests.order_by('-is_payed', 'id'),
            'drequests_stats': sorted(get_account_requests_stats(group.account), key=lambda x: x[2], reverse=True),
            'hours_left': hours,
            'minutes_left': minutes,
            # 'bonuses': totals['bonus'] if totals else [],
        }


#TODO: Denis, refactoring
@login_required
@staff_member_required
@render_to("payments/withdraw_request_decline_modal.haml")
def withdraw_request_decline_modal(request, request_id):
    wrequest = get_object_or_404(WithdrawRequest, id=request_id)
    group = wrequest.group
    form = WithrawRequestFastDeclineForm(request.POST or None, instance=wrequest)
    if request.POST and form.is_valid():
        wrequest = form.save()
        wrequest.is_payed = wrequest.is_committed = wrequest.is_ready_for_payment = False
        wrequest.closed_by = request.user
        wrequest.save()
        Logger(user=request.user, content_object=wrequest, ip=request.META["REMOTE_ADDR"], event=Events.WITHDRAW_REQUEST_FAST_DECLINED).save()
        group.process()
        return redirect('payments_account_withdraw_requests_group', wrequest.group.id)
    return {
        'form': form,
        'wrequest': wrequest,
    }


#TODO: Denis, refactoring
@login_required
@staff_member_required
@render_to("payments/requisit_view_modal.haml")
def requisit_view_modal(request, request_id):
    return {
        'r': get_object_or_404(WithdrawRequest, id=request_id),
    }


#TODO: Denis, refactoring
@login_required
@render_to("payments/any_transaction.haml")
def make_any_transaction(request):

    if not request.user.has_perm("payments.can_add_transactions"):
        raise Http404

    form = AdditionalTransactionForm(request.POST or None, request=request)

    if request.method == "POST" and form.is_valid():
        form.save()

    return {
        "form": form,
    }


@login_required
@staff_member_required
@permission_required("payments.withdrawrequest_full_access")
def export_card_withdrawals(request):
    class Echo(object):
        """An object that implements just the write method of the file-like
        interface.
        """

        def write(self, value):
            """Write the value by returning it, instead of storing in a buffer."""
            return value

    def get_results(writer):
        yield writer.writerow([item.encode('utf-8') for item in
                               (u'Заявка', u'Счёт', u'Сумма', u'Комиссия', u'Клиент получит',
                               u'Валюта')])
        # There are problems with PaymentSystemProxy and "__in" query, that's why there's Q
        for wr in WithdrawRequest.objects.filter(Q(payment_system="cards_withdrawal") |
                                                 Q(payment_system="cards_withdrawal_usd") |
                                                 Q(payment_system="cards_withdrawal_unionpay"))\
                                 .filter(is_payed=True).exclude(is_committed=True):
            result = []
            result.append(unicode(wr.pk))
            result.append(unicode(wr.account))
            result.append(unicode(wr.amount))
            commission = wr.payment_system.WithdrawForm.calculate_commission(wr).commission
            result.append(unicode(commission))
            result.append(unicode(wr.amount - commission))
            result.append(unicode(wr.currency))
            result.append(json.dumps(wr.params))

            yield writer.writerow([item.encode('utf-8') for item in result])

    writer = csv.writer(Echo())
    response = StreamingHttpResponse(get_results(writer), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="card_withdrawals{}.csv"'.format(
        datetime.now().strftime("%d%m%y")
    )
    return response


@login_required
@staff_member_required
@permission_required("payments.withdrawrequest_full_access")
def export_ecommpay_withdrawals(request):
    result = ["payment_group_id; site_id; external_id; customer_purse; amount; currency; comment"]
    for wr in WithdrawRequest.objects.filter(payment_system="ecommpay",
                                             is_payed=True, is_committed=None):
        purse_request = DepositRequest.objects.filter(payment_system="ecommpay", is_committed=True,
                                                      account__user=wr.account.user,
                                                      params__contains="transaction").order_by('-creation_ts').first()
        if purse_request:
            purse = purse_request.params["transaction"]
        else:
            purse = "ERROR! Transaction_id not found!"

        result.append('; '.join((
            "1",  # Bank cards payment group
            str(settings.ACCENTPAY_ACCOUNT),
            str(wr.id),
            str(purse),
            str(int(wr.amount * 100)),
            str(wr.currency),
            "Withdrawal from trading account #%s" % wr.account.mt4_id,
        )))

    result = '\r\n'.join(result)

    response = HttpResponse(result, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="ecommpay_withdrawals{}.csv"'.format(
        datetime.now().strftime("%d%m%y")
    )
    return response