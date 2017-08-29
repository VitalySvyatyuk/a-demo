# coding=utf-8

import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db.models import Q, Max
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, status, exceptions
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from geobase.utils import get_country
from log.models import Event
from otp.check import check_otp_drf
from otp.rest_permissions import IsOtpBinded
from payments.models import WithdrawRequest, DepositRequest, WithdrawRequestsGroup, BaseRequest
from payments.rest_serializers import WithdrawRequestSerializer, DepositRequestSerializer, BaseRequestSerializer
from payments.restricted_countries import restricted_countries_list
from payments.utils import load_payment_system, get_payment_systems
from platforms.converter import convert_currency
from platforms.models import TradingAccount
from platforms.mt4.external.models import Mt4Quote
from payments.__init__ import PAYMENT_SYSTEMS_FORMS
from transfers.forms import InternalTransferForm
from wkhtmltopdf.models import render_to_pdf

from logging import getLogger
log = getLogger(__name__)

class WithdrawRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WithdrawRequestSerializer
    permission_classes = (IsAuthenticated, IsOtpBinded,)
    paginator = None

    def get_queryset(self):
        return WithdrawRequest.objects.filter(account__user=self.request.user)

    @detail_route(methods=['post'])
    def cancel(self, request, pk=None):
        req = self.get_object()

        if not req.is_cancelable_by_user:
            raise exceptions.PermissionDenied(_('It is too late to cancel this request'))
        req.cancel()

        #recalculate requirements/close group
        req.group.process()

        return Response({
            'object': WithdrawRequestSerializer(req).data,
            'detail': _('Request successfuly canceled')
        })


class DepositRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepositRequestSerializer
    permission_classes = (IsAuthenticated, IsOtpBinded,)
    paginator = None

    def get_queryset(self):
        return DepositRequest.objects.filter(account__user=self.request.user)

    @detail_route(methods=['post'])
    def cancel(self, request, pk=None):
        req = self.get_object()

        # фин отдел подтвердил заявку
        if not req.is_cancelable_by_user:
            raise exceptions.PermissionDenied(_('It is too late to cancel this request'))
        req.cancel()
        return Response({
            'object': DepositRequestSerializer(req).data,
            'detail': _('Request successfuly canceled')
        })


class BaseRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BaseRequestSerializer
    permission_classes = (IsAuthenticated, IsOtpBinded,)
    paginator = None

    def get_queryset(self):
        return BaseRequest.objects \
            .select_related('depositrequest__account', 'withdrawrequest__account') \
            .filter(
                Q(withdrawrequest__account__user=self.request.user)
                | Q(depositrequest__account__user=self.request.user))

    @detail_route(methods=['post'])
    def cancel(self, request, pk=None):
        req = self.get_object()

        # фин отдел подтвердил заявку
        if not req.is_cancelable_by_user:
            raise exceptions.PermissionDenied(_('It is too late to cancel this request'))
        req.cancel()

        req_leaf = req.as_leaf_class()
        if isinstance(req_leaf, WithdrawRequest) and req_leaf.group:
            req_leaf.group.process()

        return Response({
            'object': BaseRequestSerializer(req).data,
            'detail': _('Request successfuly canceled')
        })


class PaymentViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, IsOtpBinded,)
    paginator = None

    @list_route()
    def init_data(self, request):
        if not request.user.accounts.alive().non_demo().exists():
            return Response({"has_no_accounts": True})
        most_recent_deposit = DepositRequest.objects \
            .filter(account__in=request.user.accounts.all()) \
            .exclude(payment_system="office").last()
        if most_recent_deposit:
            most_recent_deposit = most_recent_deposit.payment_system

        most_recent_withdraw = WithdrawRequest.objects \
            .filter(account__in=request.user.accounts.all()) \
            .exclude(payment_system="office").last()
        if most_recent_withdraw:
            most_recent_withdraw = most_recent_withdraw.payment_system

        symbols = Mt4Quote.objects \
            .filter(symbol__in=['USDEURconv', 'USDRUBconv']) \
            .only('symbol', 'bid', 'ask', 'digits')

        columns = [s[3:6] for s in symbols.exclude(symbol='USDUAHconv').values_list('symbol', flat=True)]
        columns.insert(0, u'USD')

        table = {}

        for row in [u'USD', u'RUB', u'EUR']:
            table[row] = []
            for column in columns:
                if row == column:
                    value = (1, 1)
                else:
                    if column == "XAG":
                        column = "SILVER"
                    elif column == "XAU":
                        column = "GOLD"
                    try:
                        value = (
                            round(convert_currency(1, row, column)[0], 4),
                            round(1/convert_currency(1, column, row)[0], 4),
                        )
                    except:
                        value = (0, 0)
                table[row].append(value)
        systems_list = get_payment_systems()

        # Convers payment system objects to simple object
        for op, op_data in systems_list.items():
            for psgroup, psgroup_data in op_data.items():
                for sys, sys_data in psgroup_data["systems"].items():
                    psgroup_data["systems"][sys] = {
                        'slug': sys,
                        'name': u'%s' % sys_data.name,
                        'deposit_redirect': sys_data.deposit_redirect
                    }
        return Response({
            "systems_list": systems_list,
            "most_recent": {"deposit": most_recent_deposit, "withdraw": most_recent_withdraw},
            "conversionTable": table,
            "columns": columns,
            "PAYMENTS_RECEIVER": settings.PAYMENTS_RECEIVER
        })

    @list_route()
    def payment_form(self, request):
        if settings.PAYMENTS_UNAVAILABLE:
            raise exceptions.APIException(_(u"Due to technical issues service is temporarily unavailable"))

        operation = request.query_params.get("operation") or request.data["operation"]
        account_mt4_id = request.query_params.get('account')

        # process transfer
        if operation == 'transfer':
            return Response({
                'form': InternalTransferForm(
                    request=request, account=account_mt4_id).render_form()})

        # process w/d
        ps_raw = request.query_params.get("ps") or request.data["ps"]
        try:
            ps = load_payment_system(ps_raw, request=request)
        except ImproperlyConfigured:
            raise ParseError(_(u"Invalid payment system name"))
        if ps is None or not ps.visible:
            raise ParseError(_(u"Invalid payment system name"))

        if operation == "deposit":
            return Response({
                "form": ps.DepositForm(request=request, account=account_mt4_id).render_form()
            })

        if operation == "withdraw":
            details_form = ps.DetailsForm(request=request, payment_system=ps)
            return Response({
                "form": ps.WithdrawForm(request=request, account=account_mt4_id).render_form(details_form)
            })

        raise ParseError(_(u"You should provide operation type"))

    @list_route()
    def get_commission(self, request):
        pass

    @list_route()
    def download_bank_requisits(self, request, filename="Payment order to deposit the account in the Arum Capital.pdf"):
        ps = load_payment_system(request.query_params.get("ps"))
        log.debug("Payment system=%s" % ps)
        if ps is None:
            return exceptions.NotAcceptable(_('Payment system not found'))
        form = ps.DepositForm(request.query_params, request=request)

        if not form.is_valid():
            return Response({
                'detail': _('Data is invalid')
            }, status=400)

        obj = form.save(commit=False)
        bank = map(lambda p: p[1], form.get_bank_base(obj.account))

        from geobase.models import Country
        country = Country.objects.get(pk=request.query_params.get('country')).name_en
        if ps.slug == "bankuah":
            # считаем хитрый украинский НДС
            obj.vat_amount = obj.amount / 6

        log.debug("object=%s" % obj)
        tempfile = render_to_pdf('payments/includes/bank_preview.html', {'object': obj,
                                                                         "bank": bank,
                                                                         'country': country})
        log.debug("tempfile=%s" % tempfile)
        content = open(tempfile).read()
        log.debug("Content size=%d" % len(content))
        os.remove(tempfile)


        response = HttpResponse(content, content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return response

    @list_route(methods=['post'])
    def process_deposit(self, request):
        payment_system = load_payment_system(request.data["ps"], raise_404=True, request=request)
        deposit_form = payment_system.DepositForm(data=request.data, request=request)

        if not deposit_form.is_valid():
            return Response({
                "form": deposit_form.render_form(),
            }, status=400)

        tmp = TradingAccount.objects.all().aggregate(Max('invoice_amount'))['invoice_amount__max']
        ta = TradingAccount.objects.all()
        ta.update(invoice_amount=tmp+1)

        if request.data.get("confirmed"):
            return self.process_deposit_confirmed(request, payment_system, deposit_form)
        return self.process_deposit_preview(request, payment_system, deposit_form)

    @staticmethod
    def process_deposit_confirmed(request, payment_system, form):
        from payments.utils import PaymentException

        deposit_request = form.save()
        # qiwi работает не через POST, а через GET, стало быть,
        # можно не показывать экран с редиректом, а сразу переводить на страницу
        if payment_system.slug == "qiwi":
            redirect_to = form.redirect()
            if redirect_to is None:
                return Response({
                    'detail': _('qiwi_bad_request')
                }, status=400)
            else:
                return Response({
                    'html': render_to_string("payments/instructions/qiwi.html")
                })

        elif payment_system == "mixplat":
            error_message = form.pay_init()
            if error_message:
                return Response({'detail': "Error: %s" % error_message}, status=400)
            else:
                return Response({'html': render_to_string("payments/instructions/mixplat.html")})

        elif payment_system == "pay_boutique":
            try:
                return Response({"redirect": form.redirect()})
            except PaymentException as e:
                return Response({'detail': "Error: %s" % e.message}, status=400)

        elif payment_system == "regular_pay":
            return Response({"redirect": form.redirect()})

        elif payment_system == "neteller":
            error = form.make_request()
            if error:
                return Response({'detail': "Error: %s" % error}, status=400)
            else:
                return Response({"success": True})

        elif payment_system == "webmoney" and deposit_request.amount_in_USD >= 0:
            return Response({'html': render_to_string("payments/instructions/webmoney.html")})

        elif (payment_system.slug in PAYMENT_SYSTEMS_FORMS["transfer"]
              or payment_system.slug in PAYMENT_SYSTEMS_FORMS["preview"]):
            return Response({"success": True})

        elif payment_system == "orangepay":
            return Response({"redirect": form.redirect_url})

        return Response({
            "html": render_to_string(
                "payments/quick_payment_redirect.haml",
                RequestContext(request, {
                    "form": form.mutate()
                }))
        })

    @staticmethod
    def process_deposit_preview(request, payment_system, form):
        user_country_is_restricted = False
        if payment_system.slug == 'moneybookers_cards' and \
                request.user.profile.country and \
                request.user.profile.country.code in restricted_countries_list:
            user_country_is_restricted = True

        if payment_system.slug.startswith("bank"):  # bank preview is different
            preview_items = form.save(commit=False).bank_preview_items(form=form)
        else:
            # usual systems, just dump form fields (readonly)
            preview_items = []
            from django import forms
            for x in form.visible_fields():
                field = form.fields[x.name]
                if isinstance(field, forms.ChoiceField):
                    choices = {unicode(k): v for k, v in field.choices}
                    val = choices[request.data[x.name]]
                    preview_items.append((unicode(x.label), unicode(val)))
                else:
                    preview_items.append((unicode(x.label), unicode(form.cleaned_data[x.name])))
        return Response({
            "preview_items": preview_items,
            "restricted_country": user_country_is_restricted
        })

    @list_route(methods=['post'])
    def process_withdraw(self, request):

        ps = load_payment_system(request.data["ps"], raise_404=True)

        withdraw_form = ps.WithdrawForm(request.data or None, request=request)
        details_form = ps.DetailsForm(request.data or None, request=request, payment_system=ps)
        if not (withdraw_form.is_valid() and details_form.is_valid()):
            return Response({
                "form": withdraw_form.render_form(details_form),
            }, status=400)
        if request.data.get("confirmed"):
            return self.process_withdraw_confirmed(request, ps, withdraw_form, details_form)
        return self.process_withdraw_preview(withdraw_form, details_form)

    @staticmethod
    def process_withdraw_confirmed(request, payment_system, withdraw_form, details_form):
        check_otp_drf('process_withdraw_confirmed', request)

        details = details_form.save()
        obj = withdraw_form.save(commit=False)
        obj.params = details
        obj.params['domain'] = request.get_host()

        # Auto-withdrawals for webmoney are disabled for now
        # if payment_system.slug == "webmoney":
        #     if withdraw_form.verify(obj):
        #         withdraw_form.execute(request, obj)

        group = WithdrawRequestsGroup.objects.get_next_available_for(obj.account)
        obj.group = group
        obj.save()

        ##################### AutoNoSick group logic ##################
        group.reset()
        group.process()
        ###############################################################

        return Response({
            "success": True
        })

    @staticmethod
    def process_withdraw_preview(withdraw_form, details_form):

        preview_items = []
        data = dict(withdraw_form.cleaned_data)
        data.update(details_form.cleaned_data)
        for x in withdraw_form.visible_fields() + details_form.visible_fields():
            if data[x.name]:
                if x.name == "country":
                    val = get_country(data[x.name])
                else:
                    val = data[x.name]
                preview_items.append((unicode(x.label), unicode(val)))

        return Response({
            "preview_items": preview_items
        })

    @list_route(methods=['post'])
    def process_transfer(self, request):
        form = InternalTransferForm(data=request.data or None, request=request)

        if not form.is_valid():
            return Response({
                "form": form.render_form(),
            }, status=400)
        if request.data.get("confirmed"):
            return self.process_transfer_confirmed(request, form)
        return self.process_transfer_preview(request, form)

    @staticmethod
    def process_transfer_confirmed(request, form):
        check_otp_drf('process_withdraw_confirmed', request)

        issue = form.save()
        if not issue:
            raise Exception("Cant't proccess INTERNAL_TRANSFER")

        Event.INTERNAL_TRANSFER.log(form.cleaned_data["sender"], {
            "from": form.cleaned_data["sender"].mt4_id,
            "to": form.cleaned_data["recipient"],
            "amount": float(form.cleaned_data["amount"]),
            "currency": form.cleaned_data["currency"],
            "auto": form.cleaned_data["mode"] == "auto",
        })

        return Response({
            "success": True
        })

    @staticmethod
    def process_transfer_preview(request, form):
        excluded_fields = ["mode"]

        excluded_fields += ["recipient_manual"]


        preview_items = [
            (unicode(x.label), unicode(form.cleaned_data[x.name]))
            for x in form.visible_fields()
            if x.name not in excluded_fields
        ]
        return Response({
            "preview_items": preview_items
        })

    @list_route(methods=['post'])
    def user_requesting_chargeback_issue(self, request):
        from issuetracker.models import CheckOnChargebackIssue
        from django.contrib.auth.models import User

        user = User.objects.get(username=request.user)
        issue = CheckOnChargebackIssue.objects.filter(author=user, status__in=("open", "processing")).first()
        if issue:
            issue.user_requested_check = True
            issue.save()
        else:
            new_issue = CheckOnChargebackIssue(author=user, user_requested_check=True)
            new_issue.save()

        return Response({
            'detail': _('Your documents will be checked soon')
        }, status=status.HTTP_202_ACCEPTED)

    @list_route()
    def get_chargeback_info(self, request):
        from issuetracker.models import CheckOnChargebackIssue
        from django.db.models import Q
        check_chargeback = CheckOnChargebackIssue.objects.filter(
            Q(author=request.user),
            Q(status='open') | Q(status='processing'))\
            .exists()

        has_doc = request.user.profile.has_documents()

        return Response({
            "check_chargeback": check_chargeback,
            "has_doc": has_doc,
        })
