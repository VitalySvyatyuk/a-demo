# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from copy import copy
from datetime import datetime, timedelta, date
from decimal import Decimal

from annoying.decorators import signals
from django.conf import settings
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.mail import mail_admins, send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, get_language, activate
from jsonfield.fields import JSONField
from django.contrib.postgres.fields import ArrayField

from currencies import currencies
from currencies.currencies import get_currency
from currencies.money import Money
from log.models import Logger, Events
from notification import models as notification
from payments.fields import PaymentSystemField
from payments.tasks import update_profit
from payments.utils import PaymentSystemProxy
from platforms.converter import convert_currency
from platforms.exceptions import PlatformError
from platforms.models import TradingAccount
from requisits.models import UserRequisit
from shared.models import StateSavingModel
from shared.utils import get_admin_url, upload_to
from shared.werkzeug_utils import cached_property

log = logging.getLogger(__name__)

CURRENCY_CHOICES = currencies.choices()

REASONS_TO_WITHDRAWAL = SortedDict(data=(
    ("funds", _("Withdraw the funds I earn")),
    ("money", _("In need of money")),
    ("service", _("Not satisfied with the service")),
    ("other", _("Other reasons"))
))


BASE_REQUEST_STATUSES = {
    "money_waiting": _('Money waiting'),
    "processing": _('Processing'),
    "canceled_by_client": _('Canceled by client'),
    "verification": _('Verification'),
    "money_sending": _('Money sending'),
    "done": _('Done'),
    "canceled": _('Canceled'),
}


class BaseRequest(StateSavingModel):
    """
    Base for any client deposit change request.
    """
    amount = models.DecimalField(_("Amount"), help_text=_('Example: 5.2'), max_digits=10, decimal_places=2)
    amount_money = property(lambda self: Money(self.amount, self.currency))
    conversion_rate = models.FloatField(_(u"Exchange rate at request date"), null=True, blank=True)
    payment_system = PaymentSystemField(_("Payment system"), default="", max_length=100)
    active_balance = models.DecimalField(_('Balance'), help_text=_('Balance on getting request'),
                                         max_digits=10, decimal_places=2, blank=True,
                                         null=True, editable=False)
    active_balance_money = property(lambda self: Money(self.active_balance, self.currency))
    currency = models.CharField(_("Currency"), max_length=6, choices=CURRENCY_CHOICES)
    private_comment = models.TextField(_('Internal comment'), null=True, blank=True)
    public_comment = models.TextField(_("Public comment"), blank=True, null=True)
    comment_visible = models.BooleanField(_("Manager's comment is shown to client"), default=True)
    creation_ts = models.DateTimeField(_("Creation timestamp"), editable=False, auto_now_add=True, db_index=True)
    params = JSONField(_("Details"), blank=True, null=True)

    is_payed = models.NullBooleanField(_("Is payed"))
    is_committed = models.NullBooleanField(_("Is committed"),
                                           help_text=_("When this field changes, client gets a notification"))
    # We need to store the "automatic" value in the database to allow admin
    # filtering
    _is_automatic = models.BooleanField(_("Automatically"), default=False)

    class Meta:
        ordering = ["-creation_ts"]
        get_latest_by = "creation_ts"

    def as_leaf_class(self):
        if hasattr(self, "depositrequest"):
            return self.depositrequest
        return self.withdrawrequest

    def __unicode__(self):
        return unicode(self.as_leaf_class())

    @property
    def amount_in_USD(self):
        return self.amount_money.to("USD").amount

    @property
    def is_cancelable_by_user(self):
        return not (self.is_committed is not None or self.is_payed)

    def cancel(self):
        self.is_committed = False
        self.is_payed = False
        self.public_comment = _("Request is rejected by client")
        self.save()

    @property
    def automatic(self):
        return False

    @property
    def needs_verification(self):
        return self.payment_system in settings.CHARGEBACK_PAYMENT_SYSTEMS and self.amount_in_USD >= 800

    def get_status_display(self):
        return BASE_REQUEST_STATUSES[self.status]

    def make_payment(self, comment=None):
        log.debug("Making payment ID = %s..." % self.id)
        if self.is_committed:
            log.debug("Oops, already committed; terminating")
            return

        if isinstance(self, DepositRequest):
            form = self.payment_system.DepositForm
            is_deposit = True
            self.is_committed = True  # We must take all care to not process same deposit twice
            self.save(refresh_state=True)
            c = self.payment_system.DepositForm.calculate_commission(self)
            c_full = self.payment_system.DepositForm.calculate_commission(self, full_commission=True)
            amount = c_full.amount - c_full.commission  # Will be deposited as ExternalPay
            bonus_amount = c.amount - c.commission - amount  # Commission compensation, deposited as BonusPaid
            if bonus_amount < Decimal("0.01"):
                bonus_amount = 0
        elif isinstance(self, WithdrawRequest):
            is_deposit = False
            amount = -self.amount
            bonus_amount = 0
            form = self.payment_system.WithdrawForm
        else:
            log.debug("Oops, unknown request type; terminating")
            raise TypeError("Unknown request type: %r" % type(self))

        if self.account.currency != self.currency:
            if self.conversion_rate:
                amount = float(amount) * self.conversion_rate
                bonus_amount = float(bonus_amount) * self.conversion_rate
            else:
                amount = convert_currency(amount, from_currency=self.currency, to_currency=self.account.currency)[0]
                bonus_amount = convert_currency(bonus_amount, from_currency=self.currency,
                                                to_currency=self.account.currency)[0]
                mail_admins(u"Payment request id={} processed without saved exchange rate!".format(self.pk), "")

        try:
            comment = comment or form.generate_mt4_comment(self)
        except Exception as e:
            log.debug("Oops, couldnt generate comment: %s; terminating" % unicode(e))
            comment = unicode(self.id)

        try:
            log.debug("Sending change_balance command to TradingAccount...")
            res = self.account.change_balance(amount=amount, request_id=form.generate_mt4_request_id(self),
                                              comment=comment, transaction_type="ExternalPay")
            if bonus_amount:
                self.account.change_balance(amount=bonus_amount, request_id=form.generate_mt4_request_id(self) + 'B',
                                            comment=comment, transaction_type="BonusPaid")

            if is_deposit \
                    and self.needs_verification \
                    and not (self.params.get('cardnumber') and
                             self.account.user.profile.is_card_verified(self.params['cardnumber'])):
                self.account.block(block_reason=TradingAccount.REASON_CHARGEBACK)
                self.params['chargeback_suspect'] = True
                user_profile = self.account.user.profile
                if not user_profile.manager:
                    user_profile.autoassign_manager(force=True)
                # self.account.user.gcrm_contact.add_task(u"Client's account blocked to prevent chargeback. "
                #                                          u"Monitor the situation.")

                notification.send([self.account.user], "deposit_needs_verification",
                                  {"paymentrequest": self, 'usd_amount': self.amount_money.to("USD")})

        except PlatformError as e:

            log.debug("Command change_balance failed: %s" % unicode(e))

            if is_deposit:
                self.is_committed = None
            else:
                self.is_payed = False

                send_mail(u"Withdraw request failed",
                          u"Withdraw request failed:\n"
                          u"https://%s%s\n\n"
                          u"Error: %s" % (settings.ROOT_HOSTNAME, get_admin_url(self), unicode(e)),
                          from_email=settings.SERVER_EMAIL,
                          recipient_list=[x[1] for x in settings.ADMINS])

                Logger(user=None, content_object=self, ip=None, event=Events.WITHDRAW_REQUEST_FAILED,
                       params={'error': unicode(e.args[0])}).save()
            self.save()
            raise e
        else:
            if res is not None:
                self.refresh_state()
                self.trade_id = res.get("order_id")
                self.save(refresh_state=False)
                log.debug("Payment OK. OrderID = %s" % self.trade_id)
            else:
                log.debug("Payment OK, but OrderID is unknown :(")

            Logger(user=None, content_object=self, ip=None, event=Events.WITHDRAW_REQUEST_PAYED).save()

    def save(self, **kwargs):
        if not self.pk:
            try:  # This can fail at a query to MT4 (for example Webmoney fails like this)
                self._is_automatic = self.automatic
            except:  # But we nevertheless should save it no matter what
                pass
            if self.account.currency != self.currency:
                self.conversion_rate = convert_currency(1, self.currency, self.account.currency)[0]
        if isinstance(self, DepositRequest):
            c = self.payment_system.DepositForm.calculate_commission(self)
            self.commission = c.commission
            self.currency = c.currency
        return super(BaseRequest, self).save(**kwargs)

    def get_admin_url(self):
        from shared.utils import get_admin_url

        return get_admin_url(self)


class DepositRequestQueryset(models.query.QuerySet):
    def possible_chargeback(self):
        chargeback_time = datetime.now() - timedelta(days=365)
        return self.filter(
            payment_system__in=list(settings.CHARGEBACK_PAYMENT_SYSTEMS),
            creation_ts__gte=chargeback_time,
            ).exclude(is_payed=False)

    def is_payed(self):
        return self.filter(is_payed=True)

    def is_committed(self):
        return self.filter(is_committed=True)


class DepositRequest(BaseRequest):
    old_id = models.IntegerField(blank=True, null=True)  # should be never used in queries
    purse = models.CharField(_("Purse"), max_length=50, blank=True, null=True)
    account = models.ForeignKey(TradingAccount, verbose_name=_("Account"), related_name="depositrequest",
                                help_text=_("Select one of your accounts"), null=True)

    transaction_id = models.CharField(_("Transaction id"), max_length=50, blank=True, null=True)

    objects = DepositRequestQueryset.as_manager()

    class Meta:
        verbose_name = _("Deposit request")
        verbose_name_plural = _("Deposit requests")
        ordering = ["-creation_ts", "payment_system"]

    @property
    def automatic(self):
        return self.payment_system.DepositForm.is_automatic(self)

    @property
    def is_deposit(self):
        return True

    @property
    def is_withdraw(self):
        return False

    def __unicode__(self):
        return u"%s <= %s %s using %s at %s" % (self.account, self.amount, self.currency,
                                                self.payment_system, self.creation_ts)

    @property
    def exec_time(self):
        if isinstance(self.payment_system, PaymentSystemProxy):
            try:
                return self.creation_ts + self.payment_system.time_to_deposit()
            except AttributeError:
                # has no time_to* method :(
                pass
        return ""

    @property
    def status(self):
        if self.is_payed is None:
            return "money_waiting"
        if self.is_payed and not self.is_committed:
            return "processing"
        if self.is_payed is False:
            return "canceled_by_client"
        return "done"

    def bank_preview_items(self, form):
        items = []

        currency = get_currency(self.currency)

        key = _("Sender")
        val = [self.params["name"]]

        if self.params.get("bank"):
            val.append([self.params["country"], self.params["city"], self.params["address"]])

        items.append([key, ", ".join(val)])

        if self.params.get("passport_data"):
            items.append([_("Passport data"), self.params["passport_data"]])

        key = _("Amount")
        items.append([key, currency.display_amount(self.amount)])

        for param, value in form.get_bank():
            items.append([_(param), value])

        if self.params.get("bank"):
            items.append([_("Intermediary Bank’s code"), self.params["swift"]])
            items.append([_("Payment Details"), "According to client agreement %s" % self.account.mt4_id])
        else:
            items.append([
                    _("Payment Details"),
                    u"%s №%s" % (form.get_bank_base(self.account)[5][1],self.account.mt4_id)
            ])
        return [[unicode(k), v] for k, v in items]


@signals.post_save(sender=DepositRequest)
def deposit_request_created(sender, instance, created, **kwargs):
    if kwargs.get('raw'):
        return
    if created:
        if not instance.automatic:

            users = set(Group.objects.get(name="Back office").user_set.all())
            users.add(instance.account.user)

            try:
                balance = instance.account.get_balance(instance.currency)[0]
            except PlatformError:
                log.exception('Error determining balance of account %s' %
                              instance.account.mt4_id)
                balance = None

            notification.send(users, "deposit_request_created",
                              {"paymentrequest": instance, 'balance': balance})

        if (getattr(instance.payment_system, "with_purse_only", False)
            and not instance.account.user.requisits.filter(payment_system=instance.payment_system,
                                                           purse=instance.purse).exists()):
            UserRequisit(purse=instance.purse, user=instance.account.user,
                         payment_system=instance.payment_system, params={}).save()


@signals.post_save(sender=DepositRequest)
def deposit_request_comitted(sender, instance, created, **kwargs):
    if kwargs.get('raw'):
        return
    if created:
        return
    is_committed = instance.changes.get("is_committed")
    if is_committed is None or is_committed[1] is None:
        return
    is_committed = is_committed[1]

    if is_committed:
        notification_name = "deposit_request_committed"

        # для первого проведенного ввода подтверждаем реквизит
        if instance.account.depositrequest.filter(is_committed=True).count() == 1:
            instance.account.user.requisits.filter(payment_system=instance.payment_system,
                                                   purse=instance.purse).update(is_valid=True)
    else:
        notification_name = "deposit_request_failed"
    users = set(Group.objects.get(name="Back office").user_set.all())
    users.add(instance.account.user)
    context = {"paymentrequest": instance}
    if (instance.payment_system.slug == 'moneybookers') and \
            (not instance.account.user.documents.filter(name='passport_scan').exists()):
        context['passport_scan_needed'] = True
    notification.send(users, notification_name, context)


class WithdrawRequestsGroupObjectManager(models.Manager):
    def get_next_available_for(self, mt4account):
        group, created = self.get_or_create(account=mt4account, is_closed=False)
        return group


class WithdrawRequestsGroup(StateSavingModel):
    """
    Serves as group of requests to get approvals in batch.
    """
    account = models.ForeignKey(TradingAccount, verbose_name=_('Account'), related_name='withdrawrequestgroups')
    is_closed = models.BooleanField(_("Closed"), default=False)

    processing_level = models.IntegerField(default=0)
    processing_departments = models.CharField(_("Departments"), max_length=500, default='')
    attention_list = models.ManyToManyField(User, verbose_name=_("Needs attention"))

    updated_at = models.DateTimeField(_("Updated at"), editable=False, auto_now=True)
    created_at = models.DateTimeField(_("Created at"), editable=False, auto_now_add=True)

    objects = WithdrawRequestsGroupObjectManager()

    def __init__(self, *args, **kwargs):
        kwargs["compare_to_fresh"] = True
        super(WithdrawRequestsGroup, self).__init__(*args, **kwargs)

    class Meta:
        permissions = (
            ('can_edit_approvals', _("Can edit approvals")),  # to edit managers approvals
        )
        verbose_name = _("Withdraw request group")
        verbose_name_plural = _("Withdraw request groups")

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('payments_account_withdraw_requests_group', args=(self.id,))

    @property
    def alive_requests(self):
        return self.requests.exclude(is_committed=False).order_by('is_payed', 'id')

    @cached_property
    def profit(self):
        # refresh profit. It is legacy code, so yea..
        wr = self.requests.first()
        if wr:
            from payments.tasks import update_profit
            update_profit(wr)

        params = self.account.user.profile.params
        if params:
            return params.get('profit', None)

    @property
    def profitability_deposit(self):
        params = self.account.user.profile.params
        if params:
            return params.get('profitability_deposit', None)

    @property
    def start_time(self):
        """
        Returns time of first alive
        """
        return self.alive_requests.aggregate(min=models.Min('creation_ts')).get('min', None)

    @property
    def request_time_left(self):
        req = self.alive_requests.order_by('creation_ts')[:1]
        if req:
            return req[0].exec_time - datetime.now()

    @cached_property
    def requests_sum_total(self):
        if not self.account.currency:
            raise RuntimeError('Cannot display account {0} withdraw requests summ, because account currency is {0}'.format(self.account, type(self.account.currency)))
        currency = 'USD' if self.account.currency.is_metal else self.account.currency
        amount = sum([
            wr.amount_money.to(currency).amount
            for wr in self.alive_requests
        ], 0)
        return Money(amount, currency)

    @cached_property
    def requests_sum_stats(self):
        if not self.account.currency:
            raise RuntimeError('Cannot display account {0} withdraw requests summ, because account currency is {0}'.format(self.account, type(self.account.currency)))
        with Money.convert_cache_key('autonosick_{0}'.format(date.today().strftime("%d/%m/%Y"))):
            stats = dict()
            for wr in self.alive_requests:
                m = wr.amount_money
                if wr.payment_system in stats:
                    m = m.to(stats[wr.payment_system].currency)
                if wr.payment_system not in stats:
                    stats[wr.payment_system] = m
                else:
                    stats[wr.payment_system] += m
            return {payment_system: {
                'money': money,
                'need_check': amount_needs_check(payment_system, money)
            } for payment_system, money in stats.items()}

    def process(self):
        """
        God-function to deal with all processing
        """
        if self.is_closed:
            return

        next_required_departments = self.next_required_departments()
        next_level = self.next_required_level()
        now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        #if we have no next requirements, we should complete requests
        if not next_level:
            self.attention_list.clear()
            self.processing_departments = ''

            for wr in self.requests.filter(is_committed=None).exclude(is_payed=True):
                wr._initial_instance = copy(wr)  # dirty hack to prevent possible bugs in StateSavingModel
                                                 # why? it does not create initial state if object was created, not retrieved
                is_chargable, limit = wr.is_chargable_data()
                if not is_chargable:
                    wr.is_committed = False
                    wr.private_comment = u'REJECTED: not enough funds ({limit} available) @ {now}'.format(now=now, limit=limit)
                    wr.save()
                    continue

                wr.is_payed = True
                wr.private_comment = u'AN <{now}>: Approved {by}'.format(
                    now=now,
                    by=', '.join([a.user.get_full_name() for a in self.approvals.filter(is_accepted=True)]))
                try:
                    wr.save()
                except PlatformError as e:
                    wr.private_comment = wr.private_comment or u''
                    if e.args and e.args[0] == e.NOT_ENOUGH_MONEY:
                        current_language = get_language()
                        if wr.account.user.profile.language in [l[0] for l in settings.LANGUAGES]:
                            target_language = wr.account.user.profile.language
                        else:
                            target_language = "ru"
                        activate(target_language)
                        wr.public_comment = _("Your account didn't have enough funds when the request was processed.")
                        activate(current_language)

                        wr.is_committed = False
                        wr.private_comment = u'REJECTED: not enough funds @ {now}'.format(now=now)
                    else:
                        wr.private_comment = u'NOT PROCESSED: error {0} @ {now}'.format(e.args[0], now=now)
                    wr.save()

            #okay, set flag is_ready_for_payment for each successfull request
            for wr in self.requests.filter(is_payed=True, is_ready_for_payment=False):
                wr.is_ready_for_payment = True
                wr.save()
                Logger(user=None, content_object=wr, ip=None, event=Events.WITHDRAW_REQUEST_READY_FOR_PAYMENT).save()

            #and close group
            self.is_closed = True
            Logger(user=None, content_object=self, ip=None, event=Events.WITHDRAW_REQUESTS_GROUP_CLOSED).save()

        #if we have new step in proce ssing...
        elif self.processing_level != next_level:
            self.processing_level = next_level
            self.processing_departments = ','.join(next_required_departments.keys())  # fill deps list
            self.attention_list.clear()
            self.notify_next_departments()  # fill attention list

        #if there is requirements level and it is unchanged
        # clear up lists of attention
        # repopulate users in attention list, it will remove
        # users with approvals or if we dont need em
        # also, clear up processing_departments list
        else:
            self.attention_list.clear()
            for slug, info in next_required_departments.items():
                for user in list(info['users']) + info.get('notify', list()):
                    self.attention_list.add(user)
            self.processing_departments = ','.join(next_required_departments.keys())
        self.save()

    def reset(self):
        """
        Resets all approvals. For example, on new request create.
        """
        self.processing_level = 0
        for approval in self.approvals.all():
            approval.is_accepted = False
            approval.save()
            Logger(user=None, content_object=approval, ip=None, event=Events.WITHDRAW_REQUESTS_GROUP_APPROVAL_RESET).save()
        self.save()

    def notify_next_departments(self):
        for slug, info in self.next_required_departments().items():
            url = "https://{0}{1}".format(settings.ROOT_HOSTNAME, reverse('payments_account_withdraw_requests_group', args=(self.id,)))
            email_title = u"[Site] Approve withdrawal group #{0.id}({0.requests_sum_total}): {1}".format(self, info['name'])
            email_message = (u"Withdrawal request group #{0.id}.\n"
                             u"Account: #{0.account}\n"
                             u"Link: {1}\n").format(self, url)

            if not list(info['users']):
                raise RuntimeError(
                    'Cannot send mails to users of department {name}, because users is {users}',
                    name=slug, users=info['users'])
            users = list(info['users'])
            users.extend(info.get('notify', []))

            for user in users:
                if user not in self.attention_list.all():
                    user.email_user(email_title, email_message, from_email=None)
                    self.attention_list.add(user)

    def next_required_level(self):
        """
        Calculate current priority level
        """
        for info in sorted(self.all_requirements.values(), key=lambda x: x['priority']):
            if not info['is_approved']:
                return info['priority']

    def next_required_departments(self):
        """
        Get list of next required departments slugs
        """
        priority = self.next_required_level()
        return {slug: info for slug, info in self.all_requirements.items()
                if info['priority'] == priority and
                not info['is_approved']}

    @cached_property
    def all_departments(self):
        """
        Returns information about departments with users.
        Should return all possible departments for current account.
        """
        deps = {
            'dealing': {
                'name': _("Dealing room"),
                'priority': 10,
                'users': list(User.objects.filter(groups__name="Dealing room", is_active=True, is_staff=True))},
            'back_office': {
                'name': _("Back office"),
                'priority': 10,
                'users': list(User.objects.filter(groups__name="Back office", is_active=True, is_staff=True))},
            'compliance': {
                'name': _("Compliance"),
                'priority': 10,
                'users': list(User.objects.filter(groups__name="Compliance", is_active=True, is_staff=True))},
        }
        for info in deps.values():
            if not info['users']:
                info['users'] = User.objects.filter(is_active=True, is_superuser=True)  # Fall back to admins
            info['approvals'] = self.approvals.filter(user__in=info['users'])
            info['is_approved'] = self.approvals.filter(is_accepted=True, user__in=info['users']).exists()
        return deps

    @cached_property
    def all_requirements(self):
        if not self.requests.filter(is_payed=None):
            return dict()
        deps = dict()

        # force departments calculation for sure
        # so next logic can rely on manager existence
        all_departments = self.all_departments

        def add_task(department, task, level='info'):
            if not department in deps:
                deps[department] = copy(all_departments[department])
            deps[department].setdefault('tasks', list()).extend([{'text': task, 'level': level}])

        for dep in all_departments.keys():
            add_task(dep, _("Approve withdrawal"))

        return deps


@signals.post_save(sender=WithdrawRequestsGroup)
def wrequest_group_saved(sender, instance, created, **kwargs):
    if created:
        Logger(user=None, content_object=instance, ip=None, event=Events.WITHDRAW_REQUESTS_GROUP_CREATED).save()


class WithdrawRequestsGroupApproval(StateSavingModel):
    group = models.ForeignKey(WithdrawRequestsGroup, verbose_name=_("Withdraw Requests Group"), related_name="approvals", null=True)
    user = models.ForeignKey(User, help_text=_("Who made decision"))
    updated_by = models.ForeignKey(User, editable=False, null=True, related_name="+")

    is_accepted = models.BooleanField(_("Is accepted"), default=False)
    comment = models.TextField(_("Comment"), null=True, blank=True)

    updated_at = models.DateTimeField(_("Updated at"), editable=False, auto_now=True)
    created_at = models.DateTimeField(_("Created at"), editable=False, auto_now_add=True)

    def __init__(self, *args, **kwargs):
        kwargs['compare_to_fresh'] = True
        super(WithdrawRequestsGroupApproval, self).__init__(*args, **kwargs)

    @cached_property
    def tasks(self):
        tasks = []
        for info in self.group.all_requirements.values():
            if self.user in info['users']:
                tasks.extend(info.get('tasks', []))
        return tasks

    @cached_property
    def departments(self):
        return [
            info
            for info in self.group.all_departments.values()
            if self.user in info['users']
        ]

    def departments_names(self):
        return [d['name'] for d in self.departments]


def amount_needs_check(payment_system, money):
    return False


class WithdrawRequest(BaseRequest):
    old_id = models.IntegerField(blank=True, null=True)  # should be never used in queries
    requisit = models.ForeignKey(UserRequisit,
                                 related_name="withdraw_requests", verbose_name=_("Requisit"),
                                 help_text=_("Select one of your payment details"), null=True, default=None,
                                 blank=True)
    account = models.ForeignKey(TradingAccount, verbose_name=_("Account"), related_name="withdrawrequest",
                                help_text=_("Select one of your accounts"), null=True)
    reason = models.CharField(_("Reason of withdrawal"), choices=REASONS_TO_WITHDRAWAL.iteritems(),
                              help_text=_("Choose the reason of withdrawal"), blank=True, null=True,
                              max_length=50)
    last_transaction_id = models.CharField(_("Last transaction id on this account"),
                               blank=True, null=True, max_length=127)

    group = models.ForeignKey(WithdrawRequestsGroup, verbose_name=_("Withdraw Requests Group"), related_name="requests", null=True)
    is_ready_for_payment = models.BooleanField(_("Is ready for payout"), default=False)
    closed_by = models.ForeignKey(User, verbose_name=_("Closed by"), help_text=_("Who closed the request"), null=True, blank=True)

    class Meta:
        verbose_name = _("Withdraw request")
        verbose_name_plural = _("Withdraw requests")
        ordering = ["-creation_ts", "requisit"]

    @property
    def automatic(self):
        return self.payment_system.WithdrawForm.is_automatic(self)

    @property
    def is_deposit(self):
        return False

    @property
    def is_withdraw(self):
        return True

    @property
    def exec_time(self):
        from profiles.models import UserProfile
        days = 3
        dt = self.creation_ts + timedelta(days=days)
        dt = dt.replace(hour=23)  # extend to end of the day, so we have time
        if self.creation_ts.weekday() > (5 - days):
            # add enough days to prolong it to monday
            dt += timedelta(days=2)
        return dt

    def __unicode__(self):
        return u"%s => %s %s using %s at %s" % (self.account, self.amount, self.currency,
                                                self.payment_system, self.creation_ts)

    def is_chargable_data(self):
        withdraw_limit, bonuses = self.payment_system.WithdrawForm.get_withdraw_limit_data(self.account, include_pending_requests=False)
        withdraw_limit = withdraw_limit.to(self.currency)
        return self.amount <= withdraw_limit.amount, withdraw_limit

    @property
    def status(self):
        if self.is_payed is None and self.is_committed is None:
            return "verification"
        if self.is_payed and self.is_committed is None:
            return "money_sending"
        if self.is_committed is False:
            return "canceled"
        return "done"

    @cached_property
    def is_first_requisit_operation(self):
        if 'purse' not in self.params:
            return True
        purse_json = u'"purse": "{0}"'.format(self.params.get('purse'))
        return not(
            self.account.withdrawrequest.filter(params__contains=purse_json, is_committed=True).exists() or
            self.account.depositrequest.filter(purse=self.params.get('purse'), is_committed=True).exists()
        )

    @cached_property
    def is_first_requisit_withraw(self):
        if 'purse' not in self.params:
            return True
        purse_json = u'"purse": "{0}"'.format(self.params.get('purse'))
        return not self.account.withdrawrequest.filter(params__contains=purse_json, is_committed=True).exists()


# Fucking descriptions for admin fields
WithdrawRequest._meta.get_field('is_payed'). \
    verbose_name = mark_safe(_("Money<br>withdraw<br>from account"))
WithdrawRequest._meta.get_field('is_committed'). \
    verbose_name = mark_safe(_("Money<br>paid out<br>to client"))

DepositRequest._meta.get_field('is_payed'). \
    verbose_name = mark_safe(_("Client<br>made<br>payment"))
DepositRequest._meta.get_field('is_committed'). \
    verbose_name = mark_safe(_("Money<br>deposited<br>to account"))

@signals.post_save(sender=WithdrawRequest)
def freeze_balance(sender, instance, created, **kwargs):
    if created:
        instance.active_balance = Decimal(str(instance.account.get_balance(currency=instance.currency)[0]))
        instance.save()
        update_profit(instance)


@signals.post_save(sender=WithdrawRequest)
def withdraw_request_created(sender, instance, created, **kwargs):
    if created and not instance.payment_system.is_auto("withdraw"):
        users = set(Group.objects.get(name="Back office").user_set.all())
        users.add(instance.account.user)

        try:
            balance = instance.account.get_balance(instance.currency)[0]
        except PlatformError:
            log.exception('Error determining balance of account %s' %
                          instance.account.mt4_id)
            balance = _('Error getting balance')

        notification.send(users, "withdraw_request_created",
                          {"paymentrequest": instance, 'balance': balance, "empty": {}})


@signals.post_save(sender=WithdrawRequest)
def withdraw_request_committed(sender, instance, created, **kwargs):
    if created:
        return
    is_committed = instance.changes.get("is_committed")
    if is_committed is None or is_committed[1] is None:
        return
    if is_committed[1]:
        notification_name = "withdraw_request_committed"
        if instance.requisit is not None:
            instance.requisit.is_valid = True
            instance.requisit.save()
    else:
        notification_name = "withdraw_request_failed"

    users = set(Group.objects.get(name="Back office").user_set.all())
    users.add(instance.account.user)
    notification.send(users, notification_name,
                      {"paymentrequest": instance, "empty": {}})
    if instance.is_committed:
        Logger(user=None, content_object=instance, ip=None, event=Events.WITHDRAW_REQUEST_COMMITTED).save()
    if instance.group:
        instance.group.process()


def request_verified(sender, instance, created, **kwargs):
    is_payed = instance.changes.get("is_payed")
    is_committed = instance.changes.get("is_committed")

    if (created                      # пропускаем свежесозданные экземпляры
        or is_payed is None          # или если поле is_payed не изменено
        or not instance.is_payed     # или если разрешение не было дано
        or is_committed is not None  # или если также было изменено поле is_committed
        or instance.is_committed):   # или если уже проводили платеж
        return

    instance.make_payment()


signals.post_save(sender=WithdrawRequest)(request_verified)
signals.post_save(sender=DepositRequest)(request_verified)


class TypicalComment(models.Model):
    text = models.TextField()
    creation_ts = models.DateTimeField(auto_now_add=True)

    public = models.BooleanField(default=False)
    for_deposit = models.BooleanField(default=True)
    for_withdraw = models.BooleanField(default=False)

    is_rus = models.BooleanField(default=True)

    def __unicode__(self):
        return self.text

    class Meta:
        ordering = ('-is_rus', '-creation_ts', )


class AdditionalTransaction(models.Model):

    account = models.ForeignKey(TradingAccount, verbose_name=_("Account"))
    by = models.ForeignKey(User, verbose_name=_("Author"), blank=True)
    symbol = models.CharField(_("Transaction type"), max_length=100)
    comment = models.CharField(_("Comment"), max_length=100)
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("Currency"), choices=currencies.choices(), max_length=6, null=True)

    class Meta:
        verbose_name = _("Manual transaction")
        verbose_name_plural = _("Manual transactions")


@receiver(post_migrate)
def create_permissions(sender, **kwargs):
    if sender.label != 'payments':
        return
    
    permission, created = Permission.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(AdditionalTransaction),
        codename="can_add_transactions")

    if created:
        permission.name = "Can make payment transactions"
        permission.save()
        print "Adding permission: %s" % permission


class PaymentCategory(models.Model):
    name = models.CharField(_('Name'), max_length=160)
    priority = models.PositiveSmallIntegerField(_('Priority'),
                                                default=0,
                                                help_text=_('defines order in list'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Payment category")
        verbose_name_plural = _("Payment categories")


def ps_default_languages():
    return [x for x, _ in settings.LANGUAGES]


class PaymentMethod(models.Model):
    DEPOSIT = 0
    WITHDRAW = 1

    PAYMENT_TYPES = (
        (DEPOSIT, "Deposit"),
        (WITHDRAW, "Withdraw"),
    )

    payment_type = models.PositiveSmallIntegerField(_("Payment type"),
                                                    choices=PAYMENT_TYPES,
                                                    default=0)
    name = models.CharField(_("Name"), max_length=100)
    currency = models.CharField(_("Currency"), max_length=100)
    min_amount = models.DecimalField(_("Minimum amount"),
                                     decimal_places=2,
                                     blank=True, null=True, max_digits=10)
    max_amount = models.DecimalField(_("Maximum amount"),
                                     decimal_places=2,
                                     blank=True, null=True, max_digits=10)
    commission = models.CharField(_("Commission"),
                                  max_length=150,
                                  blank=True,
                                  default="")

    max_commission = models.CharField(_("Max commision"), max_length=150, blank=True, default="")

    min_commission = models.CharField(_("Min commision"), max_length=150, blank=True, default="")

    processing_times = models.CharField(_("Processing times"),
                                        max_length=150,
                                        blank=True,
                                        default="")
    category = models.ForeignKey(PaymentCategory,
                                 verbose_name=_("Category"))
    image = models.ImageField(_('Image'),
                              blank=True,
                              null=True,
                              upload_to=upload_to('payments/logos'),
                              help_text=_('Payment system image'))
    link = models.URLField(_("Link to payment process"))
    languages = ArrayField(models.CharField(max_length=10),
                           default=ps_default_languages)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Payment method")
        verbose_name_plural = _("Payment methods")
