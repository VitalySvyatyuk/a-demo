# -*- coding: utf-8 -*-

import json

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.contrib.messages import constants as messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template.context import Context
from django.template.loader import get_template, render_to_string
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from filterspecs import PaymentSystemFilter
from geobase.utils import get_country
from payments.models import DepositRequest, WithdrawRequest, TypicalComment, WithdrawRequestsGroup, \
    AdditionalTransaction, PaymentCategory, PaymentMethod
from payments.tasks import update_profit
from profiles.models import UserDocument
from shared.admin import BaseAdmin, with_link
from shared.utils import get_admin_url, descr


def mark_success(admin, request, queryset):
    # We do not use queryset.update here for post_save to be triggered
    if not request.user.has_perm("payments.can_commit_payments"):
        admin.message_user(request, _("Your access level doesn't allow you to process payments"), level=messages.ERROR)
        return
    for item in queryset:
        item.is_payed = True
        item.save()
mark_success.short_description = _("Commit payments")


def mark_fail(admin, request, queryset):
    # We do not use queryset.update here for post_save to be triggered
    for item in queryset:
        item.is_payed = False
        item.is_committed = False
        item.save()
mark_fail.short_description = _("Mark as failed")


class DepositRequestAdmin(BaseAdmin):

    change_list_template = "admin/payments/depositrequest/change_list.html"

    def changelist_view(self, request, extra_context=None):
        qs = TypicalComment.objects.filter(for_deposit=True)
        extra_context = { 'json_comments': json.dumps({ 'public': list(qs.filter(public=True).values_list('text', flat=True)),
                                                              'private': list(qs.filter(public=False).values_list('text', flat=True)) }, ) }

        return super(DepositRequestAdmin, self).changelist_view(request, extra_context)

    class Media:
        css = {'screen': [settings.STATIC_URL +
                          'css/gcapital-ui/jquery-ui-1.8.9.custom.css']}
        js = [settings.STATIC_URL + file for file in
              ['js/jquery-1.8.0.min.js',
               'js/jquery.form.js',
               'js/jquery-ui-1.8.23.custom.min.js',
               'js/request-admin.js',
               ]
             ]

    actions = [mark_success]
    date_hierarchy = "creation_ts"
    list_display = ("id", "account_with_link", "ps_clickable",
                    "amount_with_currency", "creation_ts",
                    "is_payed", "is_committed", "public_comment", "private_comment")
    list_filter = ("creation_ts", "is_payed", "is_committed", ('payment_system', PaymentSystemFilter), "_is_automatic")

    readonly_fields = ("id", "account_with_link", "purse",
                       "payment_system", "amount_with_currency",
                       "creation_ts", "get_params", "trade_with_link")

    search_fields = ('id', 'old_id', 'purse', 'creation_ts', 'account__mt4_id',
                     'account__user__email', 'account__user__first_name',
                     'account__user__last_name')
    fieldsets = (
        (_("General"), {
           "fields": ( "account_with_link", "purse", "payment_system",
                       "amount_with_currency", "creation_ts", 'transaction_id')
        }),
        (_("Details"), {
            "fields": ("get_params", )
        }),
        (_("Status"), {
            "fields": ("is_payed", "is_committed", "trade_with_link", "public_comment", 'comment_visible', "private_comment")
        }),
    )

    def get_readonly_fields(self, request, obj):
        readonly = list(self.readonly_fields)
        if not request.user.has_perm('payments.can_commit_payments'):
            readonly.extend(['is_payed'])
        return readonly

    account_with_link = with_link("account")

    @descr(short_description=mark_safe(_("Payment system<br>(clickable)")))
    def ps_clickable(self, obj):
        return """<a id="cm-%i" class="change-committed">%s</a>""" % (obj.pk, unicode(obj.payment_system))

    @descr("amount")
    def amount_with_currency(self, obj):
        return "%s <em>%s</em>" % (obj.amount, obj.currency)

    trade_with_link = with_link("trade", _("Trade"))

    @descr("details")
    def get_params(self, obj):
        if obj.payment_system.slug == "office":
            link = "<a href='%s'>%s</a>"
            params = SortedDict()

            if obj.params["document"] is not None:
                doc = UserDocument.objects.get(id=obj.params["document"])
                params[_("scan of receipt")] = mark_safe(link % (get_admin_url(doc), doc.name))
            else:
                params[_("scan of receipt")] = mark_safe("&mdash;")

            user = User.objects.get(id=obj.params["manager"])

            params[_("manager")] = mark_safe(link % (get_admin_url(user),
                                                     user.first_name + " " + user.last_name))
        else:
            params = obj.params

        t = get_template("payments/includes/payment_request_params.html")
        return t.render(Context({"params": params}))

    def has_add_permission(self, request):
        return False


class WithdrawRequestAdmin(BaseAdmin):

    change_list_template = "admin/payments/withdrawrequest/change_list.html"

    # form = WithdrawRequestForm

    def changelist_view(self, request, extra_context=None):
        qs = TypicalComment.objects.filter(for_withdraw=True)
        extra_context = { 'json_comments': json.dumps({ 'public': list(qs.filter(public=True).values_list('text', flat=True)),
                                                              'private': list(qs.filter(public=False).values_list('text', flat=True)) }) }

        return super(WithdrawRequestAdmin, self).changelist_view(request, extra_context=extra_context)

    class Media:
        css = {'screen': [settings.STATIC_URL +
                          'css/gcapital-ui/jquery-ui-1.8.9.custom.css']}
        js = [settings.STATIC_URL + file for file in
              ['js/jquery-1.8.0.min.js',
               'js/jquery.form.js',
               'js/jquery-ui-1.8.23.custom.min.js',
               'js/request-admin.js',
               ]
             ]

    actions = [mark_success]
    list_display = ("id", "account_with_link", "payment_system_clickable", 'last_transaction_id',
                    "amount_with_currency", "creation_ts", "is_payed", "is_committed",
                    "public_comment", "private_comment")

    date_hierarchy = "creation_ts"

    list_filter = ("creation_ts", "is_payed", "is_committed", ('payment_system', PaymentSystemFilter),
                   "_is_automatic")

    search_fields = ('id', 'old_id', 'creation_ts', 'account__mt4_id', 'params',
                     'account__user__email', 'account__user__first_name',
                     'account__user__last_name')
    readonly_fields = ("id", "account_with_link", "trade_with_link", "amount_with_currency", 'last_transaction_id',
                       "creation_ts",
                       "payment_system", "get_params", "reason")

    fieldsets = (
        (_("General"), {
            "fields": ("account_with_link", "payment_system",
                       "amount_with_currency", "creation_ts", 'last_transaction_id', "reason")
        }),
        (_("Details"), {
            "fields": ("get_params", )
        }),
        (_("Status"), {
            "fields": ("is_payed", "is_ready_for_payment", "is_committed", "trade_with_link", "public_comment",
                       'comment_visible', 'private_comment')
        }),
    )

    def get_readonly_fields(self, request, obj):
        readonly = list(self.readonly_fields)
        if not request.user.has_perm('payments.can_commit_payments'):
            readonly.extend(['is_payed'])
        return readonly

    trade_with_link = with_link("trade", _("Trade"))

    @descr(short_description=mark_safe(_("Payment system<br>(clickable)")))
    def payment_system_clickable(self, obj):
        params = obj.account.user.profile.params

        style = ""

        if params and "profitability_deposit" in params:
            if params["profitability_deposit"] > 0:
                style = "background-color: LightGreen;"
        else:
            # информация обновляется
            style = "background-color: yellow;"

        update_profit(obj)

        return "<a id='cm-%i' style='%s' class='change-committed'>%s</a>" % (obj.pk, style, unicode(obj.payment_system))

    @descr(_("Sum"))
    def amount_with_currency(self, obj):
        d = {
            'amount': obj.amount,
            'currency': obj.currency,
        }
        if obj.active_balance:
            d['balance'] = obj.active_balance
            d['style'] = "style='background-color: lightBlue'" if obj.amount == obj.active_balance else ''
            return "<span %(style)s>%(amount)s <em>%(currency)s</em></span>" % d
        return "%(amount)s <em>%(currency)s</em>" % d

    @descr(_("Info"))
    def get_params(self, obj):
        from payments.models import REASONS_TO_WITHDRAWAL
        params = SortedDict()

        for k, v in obj.params.iteritems():
            if k == "reason":
                params[k] = REASONS_TO_WITHDRAWAL[v]
            elif k == "country":
                params[k] = get_country(v)
            else:
                params[k] = v

        return render_to_string("payments/includes/payment_request_params.html",
                                {"params": params}).replace("\n", "")

    account_with_link = with_link("account", _("Account"))

    def has_add_permission(self, request):
        return False


class TypicalCommentAdmin(BaseAdmin):
    list_display = ("text", "for_deposit", "for_withdraw", "public")
    list_filter = ("for_deposit", "for_withdraw", "public")


admin.site.register(DepositRequest, DepositRequestAdmin)
admin.site.register(WithdrawRequest, WithdrawRequestAdmin)
admin.site.register(TypicalComment, TypicalCommentAdmin)


class MyAttentionListFilter(SimpleListFilter):
    title = _("My attention")
    parameter_name = 'my_attention'

    def lookups(self, request, model_admin):
        return (
            ('yes', _("Needed")),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(attention_list__in=[request.user])
        return queryset


class DepsLevelListFilter(SimpleListFilter):
    title = _("Processing stage")
    parameter_name = 'processing_level'

    def lookups(self, request, model_admin):
        return (
            ('buh', _("Financial dept.")),
            ('ib_dept', _("Partnership dept.")),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(processing_departments__icontains=self.value())
        return queryset


class StatusListFilter(SimpleListFilter):
    title = _("Status")
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('needs_approval', _("Needs approval")),
            ('committing', _("Paying out")),
            ('closed', _("Closed")),
            ('open', _("Open")),
        )

    def queryset(self, request, queryset):
        if self.value() == 'needs_approval':
            return queryset.filter(requests__is_committed=None, requests__is_ready_for_payment=False).distinct()
        elif self.value() == 'committing':
            return queryset.filter(requests__is_committed=None, requests__is_ready_for_payment=True).distinct()
        elif self.value() == 'closed':
            return queryset.filter(is_closed=True)
        elif self.value() == 'open':
            return queryset.filter(is_closed=False)
        return queryset


class WithdrawRequestsGroupAdmin(BaseAdmin):
    change_list_template = 'admin/payments/withdrawrequestsgroup/change_list.html'
    date_hierarchy = 'updated_at'
    list_filter = (StatusListFilter, MyAttentionListFilter, DepsLevelListFilter)
    list_display = (
        'account_with_link', 'created_at', 'status', 'requests_time_left',
        'requests_amount', 'requests_payment_systems',
        'user_comment', 'details_with_link')
    readonly_fields = (
        'id', 'attention_list', 'account_with_link',
        'requests_amount', 'requests_payment_systems', 'requests_time_left',
        'user_comment', 'details_with_link', 'status')
    raw_id_fields = ('account',)
    account_with_link = with_link('account')

    search_fields = ('id', 'account__mt4_id', 'account__user__email')

    def get_changelist(self, request, *args, **kwargs):
        self.current_user = request.user
        return super(WithdrawRequestsGroupAdmin, self).get_changelist(request, *args, **kwargs)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['payments_awaiting'] = {}

        wrequests = []

        from itertools import groupby
        from decimal import Decimal

        for account, account_requests in groupby(WithdrawRequest.objects.filter(is_committed=None), lambda x: x.account):
            if account.balance_money is not None:
                balance = account.balance_money
                balance.amount = Decimal(balance.amount)
                for wr in account_requests:
                    balance.amount -= Decimal(wr.amount_money.to(balance.currency).amount)
                    if balance.amount > 0:
                        wrequests.append(wr)

        for wr in wrequests:
            extra_context['payments_awaiting'].setdefault(
                wr.payment_system, {}
            ).setdefault(
                wr.currency, .0
            )
            extra_context['payments_awaiting'][wr.payment_system][wr.currency] += float(wr.amount)

        return super(WithdrawRequestsGroupAdmin, self).changelist_view(request, extra_context=extra_context)

    def requests_amount(self, obj):
        if obj.alive_requests.exists():
            return obj.requests_sum_total
        else:
            return u""
    requests_amount.short_description = _("Amount")

    def requests_time_left(self, obj):
        if not obj.is_closed and obj.request_time_left:
            total_minutes = obj.request_time_left.total_seconds() / 60.0
            hours, minutes = divmod(total_minutes, 60)
            return _('{0} h. {1} m.').format(int(hours), int(minutes))
        else:
            return ''
    requests_time_left.short_description = _("Left")

    def details_with_link(self, obj):
        url = reverse('payments_account_withdraw_requests_group', args=(obj.id,))
        return _('<a onclick="winopen(\'Requests group\', \'{url}\'); return false;" href="{url}"><b>Details</b></a>').format(url=url)
    details_with_link.short_description = _("Details")
    details_with_link.allow_tags = True

    def requests_payment_systems(self, obj):
        return u'<br/>'.join({
            unicode(r.payment_system) for r in obj.alive_requests
        })
    requests_payment_systems.short_description = _("Payment systems")
    requests_payment_systems.allow_tags = True

    def status(self, obj):
        if obj.requests.filter(is_committed=None, is_ready_for_payment=False).exists():
            if obj.processing_departments:
                return _('Approvals needed') + ': {0}'.format(obj.processing_departments)
            else:
                return _('Approvals needed') + '?'

        elif obj.requests.filter(is_committed=None, is_ready_for_payment=True).exists():
            return _("Paying out to client")
        elif obj.is_closed:
            return _("Closed")
    status.short_description = _("Status")

    def user_comment(self, obj):
        try:
            return obj.approvals.get(user=self.current_user).comment or ''
        except ObjectDoesNotExist:
            return ''
    user_comment.short_description = _("Your comment")

admin.site.register(WithdrawRequestsGroup, WithdrawRequestsGroupAdmin)


class AdditionalTransactionAdmin(BaseAdmin):

    list_display = ("id", "account_with_link", "amount", "currency",
                    "author_with_link", "symbol", "comment", "trade_with_link")
    fields = ("account_with_link", "amount", "currency", "author_with_link", "symbol", "comment", "trade_with_link")
    search_fields = ("account__mt4_id", "account__user__email")
    readonly_fields = fields
    list_filter = ("symbol",)

    account_with_link = with_link("account")
    trade_with_link = with_link("trade")
    author_with_link = with_link("by")

admin.site.register(AdditionalTransaction, AdditionalTransactionAdmin)


class PaymentCategoryAdmin(BaseAdmin):
    list_display = ("id", "name", "priority")


class PaymentMethodForm(forms.ModelForm):
    languages = forms.MultipleChoiceField(
        choices=settings.LANGUAGES,
        widget=admin.widgets.FilteredSelectMultiple(is_stacked=False, verbose_name="languages"))


class PaymentMethodAdmin(BaseAdmin):
    list_display = ("id", "name", "category")
    form = PaymentMethodForm


admin.site.register(PaymentCategory, PaymentCategoryAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
