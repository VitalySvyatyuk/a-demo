# -*- coding: utf-8 -*-

import time
from datetime import datetime, time, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from ipaddr import IPv4Address, IPv4Network
from jsonfield import JSONField

from log.models import Logger, Events
from notification import models as notification
from registration.signals import user_registered
from shared.models import StateSavingModel


class UserDataViewQuotaExceeded(Exception):
    pass


class CustomerRelationship(models.Model):
    grand_user = models.OneToOneField(User, related_name='crm', null=True, db_column="user_id")
    broco_user = models.OneToOneField("BrocoUser", related_name='crm', null=True)
    last_view_ts = models.DateTimeField(u"Последний просмотр", null=True, blank=True,
                                        help_text=u'Время последнего просмотра по кнопке "Получить клиента"')

    @property
    def user(self):
        return self.grand_user or self.broco_user

    def is_broco(self):
        return (self.broco_user is not None) and (self.grand_user is None)

    @property
    def has_only_demo(self):
        if self.is_broco():
            return self.broco_user.has_only_demo
        else:
            return not self.grand_user.accounts.non_demo().exists()

    def get_name(self):
        if self.user:
            return self.user.get_full_name()
        else:
            return "Unlinked CRM object"

    def get_referral_clicks(self):
        if self.broco_user:
            return
        from referral.utils import get_clicks_for_user
        return get_clicks_for_user(self.grand_user)

    def __unicode__(self):
        return self.get_name()

    def record_access(self, user, request=None):
        customer, created = CustomerRelationship.objects.get_or_create(grand_user=user)
        self.last_view_ts = datetime.now()
        self.save()
        lim = datetime.now() - timedelta(hours=10)
        if not AccountDataView.objects.filter(customer=self,
                                              user=user,
                                              creation_ts__gte=lim).exists():
            if not AccountDataView.check_user_quota(user, request):
                raise UserDataViewQuotaExceeded()
            AccountDataView(customer=self, user=user).save()


@receiver(user_registered)
def create_crm_for_new_user(sender, **kwargs):
    CustomerRelationship.objects.get_or_create(grand_user=kwargs['user'])


class BrocoUser(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, unique=True)
    country = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)
    manager = models.ForeignKey(User, blank=True, null=True)
    has_only_demo = models.BooleanField(default=False)

    @property
    def phone_mobile(self):  # Compatibility with UserProfile
        return self.phone

    @phone_mobile.setter
    def phone_mobile(self, value):  # Compatibility with UserProfile
        self.phone = value

    def get_full_name(self):  # Compatibility with django.contrib.auth.User
        return self.name

    def profile(self):  # Compatibility with django.contrib.auth.User
        return self

    def __unicode__(self):
        return u"Broco User %s" % self.email


class BrocoAccountManager(models.Manager):
    """Mimics mt4.models.Mt4AccountManager"""
    use_for_related_fields = True

    def non_demo_active(self):
        return self.get_queryset()

    def active(self):
        return self.get_queryset()


class BrocoAccount(models.Model):
    user = models.ForeignKey(BrocoUser, related_name="accounts")
    mt4_id = models.IntegerField()
    group = models.CharField(max_length=50)
    creation_ts = models.DateTimeField()

    objects = BrocoAccountManager()

    def __unicode__(self):
        return "%d (%s)" % (self.mt4_id, self.group)


class CRMAccess(models.Model):
    """Controls access to CRM"""
    ACCESS_CHOICES = (
        (0, u"Без доступа"),
        (1, u"Только основная база"),
        (2, u"Только база Broco"),
        (3, u"Полный доступ")
    )

    user = models.OneToOneField(User, verbose_name=u"Пользователь", related_name="crm_access")
    _allowed_ips = models.CharField(u"Разрешённые IP-адреса", max_length=1000,
                                    help_text=u"Перечислять через пробел. Если указать здесь \"*\","
                                              u" то будут разрешены любые IP. Можно указывать подсети: 192.168.1.0/25")
    active = models.BooleanField(u"Активен", default=False)
    reception_access = models.BooleanField(u"Доступ для рецепшена", default=False,
                                           help_text=u"Позволяет смотреть только контакты и персонального менеджера")
    staff_access = models.BooleanField(u"Полный доступ к CRM", default=False)
    view_agent_code = models.BooleanField(u"Виден код агента", default=False,
                                          help_text=u'Добавляет колонку "Код агента"')
    view_manager = models.BooleanField(u"Виден менеджер", default=False,
                                       help_text=u'Добавляет колонку "Персональный менеджер"')
    view_partner_domains = models.BooleanField(u"Показывать данные по сайтам партнёров", default=False)
    ib_access = models.BooleanField(u"Доступ к своим IB номерам", default=False,
                                    help_text=u"Необходимо также задать счета в соответствующем поле")
    _ib_accounts = models.TextField(u"IB-аккаунты", blank=True,
                                    help_text=u"IB-аккаунты, к клиентам которых нужно дать доступ. "
                                              u"На одной строчке, через запятую")
    regional_access_demo = models.IntegerField(u"Доступ к региональной базе ДЕМО", choices=ACCESS_CHOICES,
                                               help_text=u"Необходимо также задать города и"
                                                         u" области в соответствующем поле", default=0)
    _cities_and_regions = models.TextField(u"Города и области", blank=True, help_text=u"На одной строчке, через запятую")

    @property
    def allowed_ips(self):
        return [ip for ip in self._allowed_ips.split(' ')]

    @property
    def ib_accounts(self):
        return [int(mt4_id) for mt4_id in self._ib_accounts.split(',')]

    @property
    def cities_and_regions(self):
        return [city.strip() for city in self._cities_and_regions.split(',')]

    @property
    def is_staff(self):
        return self.reception_access or self.staff_access

    @property
    def is_ib_partner(self):
        return self.ib_access

    @property
    def regional_access(self):
        return self.regional_access_demo in (1, 3)

    def __nonzero__(self):
        return self.active and (self.is_staff or self.is_ib_partner or self.regional_access)


class AccountDataView(models.Model):
    customer = models.ForeignKey('CustomerRelationship', related_name='data_views')
    creation_ts = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, verbose_name=u"Кто просмотрел")

    @staticmethod
    def check_user_quota(user, request=None, notify=True):
        """
        Security: check if a user has exceeded his user data view quota
        """
        # we're superusers, we're so special!
        if user.is_superuser:
            return True

        def _security_notification(limit_type, email=True):
            ip = request.META.get('REMOTE_ADDR') if request else None
            user_agent = request.META.get('HTTP_USER_AGENT') if request else None
            Logger(user=user, event=Events.ACCOUNT_DATA_VIEW_EXCEEDED, ip=ip, params={
                'limit_type': limit_type,
            }).save()
            if email:
                subject = "%s has exceeded his %s CRM limit" % (user.email, limit_type)
                send_mail(subject=subject,
                          message="At %s %s from IP %s with User-Agent %s" % (datetime.now(), subject, ip,
                                                                              user_agent),
                          from_email="security@grandcapital.net",
                          recipient_list=('valexeev@grandcapital.net', 'kozlovsky@grandcapital.net'))

        if user.crm_manager and user.crm_manager.daily_limit:
            daily_limit = user.crm_manager.daily_limit
        else:
            daily_limit = 300
        per_hour = daily_limit / 3.0
        per_ten = per_hour / 5.0

        view_count_last_ten_minutes = AccountDataView.objects.filter(
            user=user,
            creation_ts__gte=datetime.now() - timedelta(minutes=10)
        ).count()
        if view_count_last_ten_minutes > per_ten:
            if notify:
                _security_notification('10 minute ({} views)'.format(per_hour), email=False)
            return False

        view_count_last_hour = AccountDataView.objects.filter(
            user=user,
            creation_ts__gte=datetime.now() - timedelta(hours=1)
        ).count()
        if view_count_last_hour > per_hour:
            _security_notification('1 hour ({} views)'.format(per_hour), email=notify)
            return False

        view_count_last_day = AccountDataView.objects.filter(
            user=user,
            creation_ts__gte=datetime.now().date()
        ).count()
        if view_count_last_day > daily_limit:
            _security_notification('daily ({} views)'.format(daily_limit), email=notify)
            return False

        return True


class CallInfo(models.Model):
    customer = models.ForeignKey('CustomerRelationship', related_name='calls')
    date = models.DateTimeField(u"Дата звонка", auto_now_add=True)
    comment = models.TextField(u"Комментарий", null=True, blank=True)
    caller = models.ForeignKey(User, verbose_name=u"Звонивший менеджер")

    def get_date_string(self):
        return self.date.strftime('%d.%m.%y %H:%M')

    def __unicode__(self):
        return u"Звонок клиенту %s %s" % (unicode(self.customer.get_name()), self.get_date_string())

    class Meta:
        get_latest_by = "date"


class LinkRequest(StateSavingModel):
    customer = models.ForeignKey('CustomerRelationship', related_name='link_requests')
    account = models.ForeignKey('platforms.TradingAccount', related_name='link_requests')
    date = models.DateTimeField(u"Дата заявки", auto_now_add=True)
    comment = models.TextField(u"Комментарий", null=True, blank=True)
    author = models.ForeignKey(User, verbose_name=u"Автор заявки")
    automatic = models.BooleanField(u"Автомат. заявка", default=False, editable=False)
    processed = models.BooleanField(u"Обработана", default=False)
    completed = models.BooleanField(u"Исполнена", default=False)

    def get_date_string(self):
        return self.date.strftime('%d.%m.%y %H:%M')

    def __unicode__(self):
        return u"Заявка на прикрепление %s %d %s" % (unicode(self.customer.get_name()),
                                                     self.account.mt4_id, self.get_date_string())

    class Meta:
        get_latest_by = "date"

    def save(self, *args, **kwargs):
        if 'processed' in self.changes and self.processed and not self.completed\
                and self.author.crm_manager.ib_account:
            agent_account = self.author.crm_manager.ib_account
            self.account.change_agent_account(agent_account)
            self.completed = True
        return super(LinkRequest, self).save(*args, **kwargs)


class CRMComment(models.Model):
    customer = models.ForeignKey('CustomerRelationship', related_name="comments")
    creation_ts = models.DateTimeField(auto_now_add=True)
    text = models.TextField(u"Текст комментария")
    author = models.ForeignKey(User, verbose_name=u"Автор")

    class Meta:
        get_latest_by = "creation_ts"


class PlannedCall(models.Model):
    customer = models.ForeignKey('CustomerRelationship', related_name='planned_calls')
    manager = models.ForeignKey(User, related_name='next_calls', null=True)
    date = models.DateField(u"Дата звонка", db_index=True)

    def get_date_string(self):
        return self.date.strftime('%d.%m.%Y')

    def get_date_from_string(self, string):
        self.date = datetime.strptime(string, '%d.%m.%Y')

    def __unicode__(self):
        return u"Планируемый звонок клиенту %s %s" % (unicode(self.customer.get_name()), self.get_date_string())

    class Meta:
        get_latest_by = "date"


class ReceptionCall(models.Model):
    DEPARTMENTS = (
        ('personal manager', u"Персональный менеджер"),
        ('tech support', u"Тех.поддержка"),
        ('free education', u"Бесплатное обучение"),
        ('fsfr', u"ФСФР"),
        ('financial department', u"Финансовый отдел"),
        ('marketing department', u"Отдел маркетинга"),
        ('partner department', u"Партнёрский отдел"),
        ('tesla', u"Тесла"),
        ('it department', u"Программисты"),
        ('other', u"Другое"),
    )
    switch_to = models.CharField(u'Перевести на', choices=DEPARTMENTS, max_length=100, blank=False, default='personal manager')
    name = models.CharField(u'ФИО', max_length=250, blank=True)
    account = models.IntegerField(u'Номер счёта', null=True, blank=True)
    company = models.CharField(u'Компания', max_length=250, blank=True)
    phone = models.CharField(u'Телефон', max_length=50, blank=True)
    applied = models.BooleanField(u'Записался на обучение', default=False)
    manager_assigned = models.BooleanField(u'Менеджер присвоен автоматически', default=False)
    description = models.TextField(u'Описание', blank=True)
    lesson_date = models.DateField(u'На какое записался', null=True, blank=True)
    experienced = models.BooleanField(u'С опытом', default=False)

    class Meta:
        permissions = (
            ("reception_call", "Allows access to reception call form"),
        )


class FinancialDepartmentCall(models.Model):
    callee = models.ForeignKey(User, verbose_name=u"Принявший звонок")
    name = models.CharField(u"Имя звонившего", max_length=250)
    account = models.IntegerField(u"Номер счёта", null=True)
    description = models.TextField(u"Описание звонка")
    date = models.DateTimeField(u"Дата и время звонка", auto_now_add=True)

    class Meta:
        permissions = (
            ('financial_dpt_call', "Allows access to financial department call form"),
        )


class PersonalManagerObjectManager(models.QuerySet):
    def active(self):
        return self.filter(user__is_active=True)

    def autoassignable(self):
        return self.filter(can_be_auto_assigned=True)

    def by_country_state(self, country, state):
        q = Q()
        if country:
            q |= Q(country_state_names__icontains=country.name_ru)
        if state:
            q |= Q(country_state_names__icontains=state.name_ru)
        return self.filter(q)

    def by_agent_code(self, ib_account):
        if not ib_account:
            self
        return self.active().filter(ib_account=ib_account)

    def working(self):
        return self.filter(
            Q(works_with_ib=True) |
            Q(can_be_auto_assigned=True) |
            Q(can_request_new_customers=True)
        )

    def works_with_office(self):
        return self.filter(works_with_office_clients=True)

    def by_language(self, language):
        return self.filter(languages__contains=language)

    def partnership(self):
        return self.filter(works_with_ib=True)

    def local(self):
        return self.filter(office=None)

    def our_office_or_local(self):
        return self.filter(Q(office__is_our=True) | Q(office=None))

    def not_our_office(self):
        return self.filter(office__is_our=False)


class PersonalManager(models.Model):
    user = models.OneToOneField(User, related_name='crm_manager')
    can_see_all_users = models.BooleanField(_("Has access to all clients"), default=False)
    is_office_supermanager = models.BooleanField(_("Office head"), default=False,
                                                 help_text=_("Can manage office's clients"))
    last_assigned = models.DateTimeField(_("Date and time of the last client assignment"), auto_now_add=True)
    can_be_auto_assigned = models.BooleanField(_("Auto"), help_text=_("Can be assigned to clients automatically"),
                                               default=False)
    can_request_new_customers = models.BooleanField(_("NEXT button"), default=False,
                                                    help_text=_("Can get client through the NEXT button"))
    can_set_agent_codes = models.BooleanField(_("Agent code"), default=False,
                                              help_text=_('Can set agent codes'))
    needs_call_check = models.BooleanField(_("Verify calls"), default=True,
                                           help_text=_("Verify that the manager calls the clients they get"))

    allowed_ips = models.CharField(u"IP", max_length=1000,
                                   help_text=_("Allowed IP-addresses. Separated by spaces. Specify \"*\" to "
                                               "allow any IP. Subnets can be specified: 192.168.1.0/25"))

    daily_limit = models.PositiveIntegerField(_("Day limit"), blank=True, null=True,
                                              help_text=_("How much clients per day can be viewed. If not specified, a "
                                                          "default value is used. WARGNING: if you increase this limit "
                                                          "make sure that the manager has at least IP filter enabled"))

    ib_account = models.PositiveIntegerField(_("IB account number"), null=True, blank=True)
    office = models.ForeignKey("crm.RegionalOffice", verbose_name=_("Office"), related_name="managers", blank=True,
                               null=True)
    reassign_agent_code_to_office = models.BooleanField(_("Change agent code to the office"), default=False,
                                                        help_text=_("If a user registers with the manager's agent code,"
                                                                    " change it to the office's agent code"))
    works_with_office_clients = models.BooleanField(
        _("Works with the office"),
        help_text=_("Works with the clients of the office"),
        default=True)
    languages = models.CharField(_("Works with languages"), max_length=10, default="ru", blank=True,
                                 help_text=_("Comma-separated language codes, e.g. ru,en,zh-cn"))
    country_state_names = models.TextField(
        _("Countries/Regions"),
        help_text=_("Names of countries and regions, separated by spaces. In English."),
        blank=True,
        default=u'')

    has_document_access = models.BooleanField(default=False, verbose_name=_("Can view uploaded documents"))

    # telephony settings
    sip_name = models.CharField(u"SIP login", max_length=1000, null=True, blank=True)
    can_see_all_calls = models.BooleanField(_("Can view all calls"), default=False)

    #
    worktime_start = models.TimeField(_("Start of the shift"), default=time(9, 0, 0))
    worktime_end = models.TimeField(_("End of the shift"), default=time(16, 0, 0))
    force_tasks_full_day = models.BooleanField(
        _("Set tasks for the whole day"),
        help_text=_("Force all the tasks to be set for the whole day"),
        default=False)

    # vacation control
    is_on_vacancies = models.BooleanField(_("On vacation"), default=False)
    on_vacancies_until = models.DateField(_("On vacation until"), null=True, blank=True)
    substitute = models.ForeignKey('self', verbose_name=_("Substitute for the vacation"), null=True, blank=True)

    # amoCRM internal logic values
    amo_id = models.IntegerField(u"AmoID", null=True, blank=True)
    amo_unsynced = models.BooleanField(u"Needs sync", default=True)
    amo_synced_at = models.DateTimeField(u"Last sync date", blank=True, null=True)

    # unused field as of amoCRM integration
    works_with_ib = models.BooleanField(u"Works with IB partners", default=False)

    objects = PersonalManagerObjectManager.as_manager()

    class Meta:
        verbose_name = _("Manager")
        verbose_name_plural = _("Managers")
        permissions = (
            ("view_all_clients", "Can see all clients in CRM"),
        )

    def __unicode__(self):
        return "%s (%s)" % (
            self.user.get_full_name(),
            unicode(self.office) if self.office else u"Main office")

    def get_country_state_list(self):
        return [e.strip() for e in self.country_state_names.split(',')]

    def is_ip_allowed(self, ip):
        from django.conf import settings
        if settings.DEBUG:
            return True
        allowed_ips = self.allowed_ips.split(' ')
        if u'*' in allowed_ips:
            return True

        for ip_net in allowed_ips:
            if IPv4Address(ip) in IPv4Network(ip_net):
                return True
        return False

    def get_today_users(self):
        from profiles.models import UserProfile
        today = datetime.today()
        date_range = (
            datetime.combine(today, time.min),
            datetime.combine(today, time.max))
        return UserProfile.objects.filter(manager=self.user, user__date_joined__range=date_range)

    def get_yesterday_users(self):
        from profiles.models import UserProfile
        yesterday = datetime.today() - timedelta(1)
        date_range = (
            datetime.combine(yesterday, time.min),
            datetime.combine(yesterday, time.max))
        return UserProfile.objects.filter(manager=self.user, user__date_joined__range=date_range)

    def get_week_users(self):
        from profiles.models import UserProfile
        today = datetime.today()
        start = today - timedelta(today.weekday())
        date_range = (
            datetime.combine(start, time.min),
            datetime.combine(today, time.max))
        return UserProfile.objects.filter(manager=self.user, user__date_joined__range=date_range)

    @property
    def is_head_supermanager(self):
        return self.is_office_supermanager and (self.office is None)

    @property
    def ib_clients(self):
        return User.objects.filter(
            profile__ib_manager=self.user
        ).order_by('-id')

    @property
    def clients(self):
        return User.objects.filter(
            profile__manager=self.user
        ).order_by(
            '-profile__assigned_to_current_manager_at',
            '-profile__taken_by_manager_at'
        )

    @property
    def clients_taken(self):
        return self.clients.exclude(
            profile__taken_by_manager_at=None
        )

    @property
    def language_list(self):
        return self.languages.split(',')

    @staticmethod
    def manager_stats(managers, date_from=None, date_to=None):
        from itertools import groupby
        from currencies.money import Money, NoneMoney
        from decimal import Decimal
        from telephony.models import CallDetailRecord
        from payments.models import DepositRequest, WithdrawRequest
        from log.models import Event
        from django.db.models import Count, Sum
        from gcrm.models import Contact

        def qs_filters(date_field):
            filters = {}
            if date_from and date_to:
                filters[date_field+'__range'] = (date_from, date_to)
            return filters

        managers = {m.id: m for m in managers}

        data = {row['manager']: {
            'manager': managers[row['manager']],
            'calls': {
                'answered': {
                    'count': 0,
                    'duration': 0
                },
                'not_answered': {
                    'count': 0,
                    'duration': 0
                },
                'totals': {
                    'count': 0,
                    'duration': 0
                }
            },
            'contacts': {
                'totals': row['count'],
                'by_button': 0
            },
            'payments': {
                'deposit': 0,
                'withdraw': 0,
                'totals': 0,
            }
        } for row in Contact.objects.filter(manager__in=managers.keys()).values('manager').annotate(count=Count('id'))}

        # CALLS
        calls_a = CallDetailRecord.objects.filter(user_a__in=data.keys(), **qs_filters('call_date')).values('user_a')
        calls_b = CallDetailRecord.objects.filter(user_b__in=data.keys(), **qs_filters('call_date')).values('user_b')

        for call in calls_a.answered().annotate(duration=Sum('duration'), count=Count('id')):
            data[call['user_a']]['calls']['answered']['count'] = call['count']
            data[call['user_a']]['calls']['answered']['duration'] = call['duration']

        for call in calls_b.answered().annotate(duration=Sum('duration'), count=Count('id')):
            data[call['user_b']]['calls']['answered']['count'] += call['count']
            data[call['user_b']]['calls']['answered']['duration'] += call['duration']

        for call in calls_a.not_answered().annotate(duration=Sum('duration'), count=Count('id')):
            data[call['user_a']]['calls']['not_answered']['count'] = call['count']
            data[call['user_a']]['calls']['not_answered']['duration'] = call['duration']

        for call in calls_b.not_answered().annotate(duration=Sum('duration'), count=Count('id')):
            data[call['user_b']]['calls']['not_answered']['count'] += call['count']
            data[call['user_b']]['calls']['not_answered']['duration'] += call['duration']

        for row in data:
            data[row]['calls']['totals']['count'] = data[row]['calls']['answered']['count'] + data[row]['calls']['not_answered']['count']
            data[row]['calls']['totals']['duration'] = data[row]['calls']['answered']['duration'] + data[row]['calls']['not_answered']['duration']

        # CONTACTS
        contacts_by_button = Event.GCRM_MANAGER_CHANGED_BY_BUTTON.qs\
            .filter(user__in=data.keys(), **qs_filters('at')).values('user').annotate(count=Count('id'))
        for contacts in contacts_by_button:
            data[contacts['user']]['contacts']['by_button'] = contacts['count']

        # $$$
        deposits = DepositRequest.objects.filter(
                account__user__gcrm_contact__manager__in=data.keys(),
                is_committed=True, **qs_filters('creation_ts'))\
            .order_by('account__user__gcrm_contact__manager') \
            .values('currency', 'account__user__gcrm_contact__manager').annotate(amount_total=Sum('amount'))

        withdraws = WithdrawRequest.objects.filter(
                account__user__gcrm_contact__manager__in=data.keys(),
                is_committed=True, **qs_filters('creation_ts'))\
            .order_by('account__user__gcrm_contact__manager') \
            .values('currency', 'account__user__gcrm_contact__manager').annotate(amount_total=Sum('amount'))

        with Money.convert_cache_key('ololo'):
            for manager, reqs in groupby(deposits, lambda x: x['account__user__gcrm_contact__manager']):
                total = Decimal(0)
                for req in reqs:
                    m = Money(req['amount_total'], req['currency']).to_USD()
                    if not isinstance(m, NoneMoney):
                        total += Decimal(m.amount)
                data[manager]['payments']['deposit'] = total
                data[manager]['payments']['totals'] = total

            for manager, reqs in groupby(withdraws, lambda x: x['account__user__gcrm_contact__manager']):
                total = Decimal(0)
                for req in reqs:
                    m = Money(req['amount_total'], req['currency']).to_USD()
                    if not isinstance(m, NoneMoney):
                        total += Decimal(m.amount)
                data[manager]['payments']['withdraw'] = total
                data[manager]['payments']['totals'] -= total
        return data.values()


class AmoObjectManager(models.Manager):
    def deleted(self):
        return self.get_queryset().filter(deleted=True)

    def active(self):
        return self.get_queryset().filter(deleted=False)

    def unsynced(self):
        return self.get_queryset().exclude(sync_at=None)


class AmoObject(models.Model):
    class Meta:
        abstract = True
    oid = models.BigIntegerField(u"Идентификатор в AmoCRM", null=True)
    sync_at = models.DateTimeField(u"Дата следующей синхронизации", default=datetime.now, null=True)
    deleted = models.BooleanField(u"Удалён", default=False)
    synced_at = models.DateTimeField(u"Дата последней синхронизации", null=True)

    objects = AmoObjectManager()

    @property
    def is_new(self):
        return self.oid is None

    # def delete(self, conn):
    #     raise NotImplementedError("toodleydooo")
        #if not self.is_new:
        #    obj = self.obj(conn=conn)
        #    if obj:
        #        obj.delete(conn=conn)
        #super(AmoObject, self).delete()

    def obj(self, conn, refresh=False):
        """It is not property to make dev able to refresh record"""
        if self.is_new:
            return None
        if self._amo_obj is None or refresh:
            # function to retrieve object depends on object type
            if isinstance(self, AmoContact):
                self._amo_obj = conn.contact_get(self.oid)
            elif isinstance(self, AmoTask):
                self._amo_obj = conn.contact_task_get(self.oid)
            elif isinstance(self, AmoNote):
                self._amo_obj = conn.contact_note_get(self.oid)
        return self._amo_obj or {}
    _amo_obj = None

    def get_amo_json(self, conn):
        """"Generate amoCRM APIv2 JSON to sync this object"""
        # activate ru-lang: we should fill amo objects with russian texts
        prev_lang = translation.get_language()
        if prev_lang != 'ru':
            translation.activate('ru')

        # fill object with fresh data
        res = self._to_amo_json(conn, dict() if self.is_new else self.obj(conn=conn))

        # revert language
        if prev_lang != 'ru':
            translation.activate(prev_lang)
        return res

    def _to_amo_json(self, conn, obj):
        raise NotImplementedError("...")

    def post_sync(self, is_new, conn):
        pass


class AmoContact(AmoObject):
    user = models.OneToOneField(User, verbose_name=u"Пользователь сайта", related_name="amo", on_delete=models.SET_NULL, null=True)

    def get_url(self):
        return self.user.gcrm_contact.get_absolute_url()
        # if self.oid:
        #     return "https://grandcapital.amocrm.ru/private/contacts/edit.php?ID=%s" % self.oid

    def add_task(self, type, text, assignee, at=None, force_time=None):
        assert assignee.crm_manager

        if assignee.crm_manager.force_tasks_full_day:
            force_time = time(23, 59, 59)

        from crm.utils import calculate_finish_time
        finish = calculate_finish_time(assignee, at=at, force_time=force_time)

        # get_or_create 4 sure
        try:
            task, created = AmoTask.objects.get_or_create(
                contact=self,
                type=type,
                text=text,
                assignee=assignee,
                finish=finish)
            return task
        except MultipleObjectsReturned:
            pass

    def add_note(self, text):
        return AmoNote.objects.create(contact=self, text=text)

    def set_all_unsynced(self):
        self.sync_at = datetime.now()
        self.save()

    def get_last_activity(self):
        mt4_dates = [mt4user.lastdate for mt4user in self.user.accounts.alive_mt4_users()]
        mt4_last_date = max(mt4_dates) if mt4_dates else None

        act_at = self.user.last_login
        act_name = u"Логин на сайт"
        if mt4_last_date and mt4_last_date > act_at:
            act_at = mt4_last_date
            act_name = u"Логин МТ4"

        logs = self.get_last_activities()
        if logs and (act_at is None or logs[0].at > act_at):
            act_at = logs[0].at
            act_name = logs[0].get_event_display()
        return act_at, act_name

    def get_last_activities(self):
        return self.user.log.filter(event__in=[
            Events.PASSWORD_RESTORED,
            Events.PROFILE_CHANGED,
            Events.DOCUMENT_UPLOADED,
            Events.OTP_BINDING_CREATED,
            Events.ACCOUNT_CREATED,
            Events.ACCOUNT_DELETED,
            Events.ACCOUNT_PASSWORD_RESTORED,
            Events.LEVERAGE_CHANGED,
            Events.WEBTRADER_LOGIN,
            Events.DEPOSIT_REQUEST_CREATED,
            Events.WITHDRAW_REQUEST_CREATED,
            Events.INTERNAL_TRANSFER,
            Events.EDUCATION_PAYMENT,
            Events.CONSULTATION_PAYMENT,
            Events.REPLICATION_RATIO_CHANGED,
            Events.NOTIFICATION_RATIO_CHANGED,
            Events.PAMM_STATUS_UPDATE,
            Events.MINIMAL_EQUITY_CHANGED,
            Events.MAX_LOSSES_REACHED,
            Events.VPS_SUBSCRIPTION,
        ]).order_by('-at')

    def _to_amo_json(self, conn, obj):
        obj['request_id'] = str(self.id)
        profile = self.user.profile
        assert len(unicode(profile)) > 0

        try:
            partner_program = self.user.partner_program
        except ObjectDoesNotExist:
            partner_program = None

        addr = map(unicode, filter(lambda x: x, [
            profile.country, profile.state, profile.city
        ]))
        name = filter(lambda x: x, [
            profile.user.first_name,
            profile.middle_name,
            profile.user.last_name
        ]) or unicode(profile)

        # activity log sources
        logs = self.get_last_activities()
        last_activity = self.get_last_activity()
        last_activities = [last_activity[1]]  # first - last activity
        last_activities.extend([
            l.get_event_display()
            for l in logs.filter(at__lt=last_activity[0])[:3]
        ])

        obj['name'] = u' '.join(name)

        # setup dates in respect of our db
        obj['date_create'] = time.mktime(self.user.date_joined.timetuple())
        obj['last_modified'] = time.mktime(datetime.now().timetuple())
        if profile.manager:
            obj['responsible_user_id'] = profile.manager.crm_manager.amo_id
        else:
            obj['responsible_user_id'] = 109672  # Marwin!
        obj.setdefault('custom_fields', []).extend([{
            "id": conn.contact_field_id('PHONE'),
            "values": [{
                "value": "usr%s" % self.user.id,
                "enum": "OTHER"
            }],
        }, {
            "id": conn.contact_field_id('ADDRESS'),
            "values": [{
                "value": u', '.join(addr),
            }],
        }, {
            "id": 552906,  # regdate
            "values": [{
                "value": self.user.date_joined.strftime("%d.%m.%Y"),
            }],
        }, {
            "id": 552908,  # activity
            "values": [{
                "value": last_activity[0].strftime("%d.%m.%Y"),
            }],
        }, {
            "id": 552910,  # activity info
            "values": [{
                "value": u', '.join(last_activities),
            }],
        }, {
            "id": 715862,  # partner program
            "values": [{
                "value": partner_program.program_type if partner_program else '',
            }],
        }, {
            "id": 716230,  # partner program model id
            "values": [{
                "value": partner_program.id if partner_program else '',
            }],
        }, {
            "id": 716232,  # partner program id
            "values": [{
                "value": partner_program.program_id if partner_program else '',
            }],
        }])

        tags = {
            tag['name']
            for tag in obj['tags']} if 'tags' in obj else set()
        tags.update([
            unicode(a.group.name)
            for a in self.user.accounts.all() if a.group])
        if profile.registered_from:
            tags.add(profile.registered_from)
        if profile.country:
            tags.add('Russian' if profile.country.is_russian_language else 'English')
            if self.user.accounts.real_ib().exists():
                tags.add('Real IB {}'.format('Russian' if profile.country.is_russian_language else 'English'))

        obj['tags'] = u', '.join(tags)
        return obj

    def post_sync(self, is_new, conn):
        if is_new:
            from crm.pyamo2.utils import easy_amo_note, contact_is_lead
            for query in [self.user.email, self.user.profile.phone_mobile]:
                if query and len(query) > 4:  # to forget about '+7' numbers
                    data = conn.contacts_get(query=query)
                    if data:
                        for contact in data.values():
                            if contact_is_lead(contact):
                                note = easy_amo_note(conn, contact['id'], u"Новый ПОХОЖИЙ ЛК: %s" % (self.get_url(),))
                                conn.contact_notes_set([note])

            # create notification for manager
            if self.user.profile.manager:
                Notification(
                    user=self.user.profile.manager,
                    type='new_client',
                    text=self.user.get_full_name(),
                    params={'user_id': self.user.id},
                ).save()

    # def delete(self, conn=None):
    #     "if we should remove contact, we should remove every related deal"
    #     for deal in self.deals.all():
    #         deal.delete(conn)

    #     #remove contact itself
    #     super(AmoContact, self).delete(conn)

    # def try_attach_to_lead(self, conn, obj):
    #     "Try to find lead contact with same email and use id to sync"
    #     raise NotImplementedError("rework it")
    #     pager = conn.find_contacts(self.user.email)
    #     for cont in pager.iter():
    #         emails = [e['value']for e in cont.emails]
    #         if self.user.email in emails:
    #             obj.id = cont.id
    #             return cont


class AmoTask(AmoObject):
    contact = models.ForeignKey(AmoContact, verbose_name=u"Контакт AmoCRM", related_name="tasks", null=True)
    TASK_OBJ_TYPES = (
        ('CALL', u'Звонок'),
        ('LETTER', u"Письмо"),
        ('MEETING', u"Встреча"),
        ('3250', u'Первая связь'),
    )
    type = models.CharField(u"Тип", choices=TASK_OBJ_TYPES, default='CALL', max_length=255)
    assignee = models.ForeignKey(User, verbose_name=u"Исполнитель", related_name="amo_tasks", null=True)
    text = models.TextField(u"Текст")
    finish = models.DateTimeField(u"Выполнить до")
    created_at = models.DateTimeField(u"Дата создания", auto_now_add=True)
    last_modified = models.DateTimeField(u"Последнее изменение", auto_now_add=True)
    is_completed = models.BooleanField(u"Завершена", default=False)

    # def delete(self, conn=None):
    #     self._conn = conn or self._conn
    #     if not self.is_new():
    #         obj = self.obj(conn=self._conn)
    #         if obj:
    #             obj.delete()
    #     super(AmoObject, self).delete()

    def _to_amo_json(self, conn, obj):
        obj['request_id'] = str(self.id)
        # skip sync of task if contacts wasn't synced yet
        if self.contact and self.contact.is_new:
            return

        if self.is_new:
            obj['element_id'] = self.contact.oid
            obj['element_type'] = 1  # contact
            obj['task_type'] = self.type
            obj['text'] = self.text
            try:
                obj['responsible_user_id'] = self.assignee.crm_manager.amo_id
            except ObjectDoesNotExist:
                obj['responsible_user_id'] = 109672  # Marwin!
            obj['complete_till'] = time.mktime(self.finish.timetuple())
        else:
            assert obj
            try:
                self.contact = AmoContact.objects.get(oid=int(obj['element_id']))
            # possible lead contact
            except ObjectDoesNotExist:
                pass
            self.type = obj['task_type']
            self.text = obj['text']
            self.created_at = datetime.fromtimestamp(obj['date_create'])
            self.last_modified = datetime.fromtimestamp(obj['last_modified'])
            self.finish = datetime.fromtimestamp(obj['complete_till'])
            try:
                self.assignee = PersonalManager.objects.get(amo_id=int(obj['responsible_user_id'])).user
            except ObjectDoesNotExist:
                pass
            self.is_completed = str(obj['status']) == '1'
        return obj


class AmoNote(AmoObject):
    contact = models.ForeignKey(AmoContact, verbose_name=u"Контакт AmoCRM", related_name="notes")
    text = models.TextField(u"Текст")

    def _to_amo_json(self, conn, obj):
        obj['request_id'] = str(self.id)
        assert self.contact
        # skip sync of task if contacts wasn't synced yet
        if self.contact.is_new:
            return

        obj['element_id'] = self.contact.oid
        obj['element_type'] = 1  # contact
        obj['note_type'] = 4  # just note
        obj['text'] = self.text
        obj['responsible_user_id'] = 109672  # Marwin!
        return obj


class ManagerReassignRequest(StateSavingModel):
    author = models.ForeignKey(User, verbose_name=_("Request author"), related_name='+')
    user = models.ForeignKey(User, verbose_name=_("Client"), related_name='+')
    # managers
    previous = models.ForeignKey(User, verbose_name=_("Previous manager"), related_name='+', null=True, blank=True)
    assign_to = models.ForeignKey(User, verbose_name=_("Assign to"), related_name='+', null=True, blank=True)

    completed_by = models.ForeignKey(User, verbose_name=_("Processed"), related_name='+', null=True, blank=True)

    comment = models.TextField(_("Comment"), null=True, blank=True)
    reject_reason = models.TextField(_("Rejection reason"), null=True, blank=True)

    STATUS_TYPES = (
        ('new', _("New")),
        ('accepted', _("Approved")),
        ('rejected', _("Declined")),
    )
    status = models.CharField(_("Status"), choices=STATUS_TYPES, default='new', max_length=255)

    created_at = models.DateTimeField(_("Creation date"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Changed at"), auto_now=True)

    class Meta:
        verbose_name = _("Manager reassign request")
        verbose_name_plural = _("Manager reassign requests")
        get_latest_by = "created_at"

    def __unicode__(self):
        return u"Request #{0} for {1}: {2} -> {3}".format(
            self.id,
            self.user,
            self.previous if self.is_completed else self.user.profile.manager,
            self.assign_to)

    @property
    def is_completed(self):
        return self.status in ['accepted', 'rejected']

    @property
    def user_crm_url(self):
        return self.user.profile.get_amo().get_url()

    @property
    def current(self):
        """Return current manager"""
        return self.user.profile.manager

    @property
    def is_local(self):
        """Is it a local reassignment: from X region manager to X region manager"""
        return ((self.assign_to and self.current) and
                (self.current.crm_manager.office == self.assign_to.crm_manager.office))

    def accept(self, completed_by, notify=False, completed_by_ip=None):
        self.status = 'accepted'
        self.completed_by = completed_by
        self.previous = self.user.profile.manager
        self.user.profile.set_manager(self.assign_to)
        self.save()

        if notify:
            to = [self.author]
            if self.assign_to:
                to.append(self.assign_to)
            notification.send(to, 'crm_reassignrequest_accepted', {'obj': self})

        Logger(user=completed_by, ip=completed_by_ip,
               content_object=self.user, event=Events.MANAGER_REASSIGN_REQUEST_ACCEPTED,
               params={"request_id": self.id, "request_str": unicode(self)}
               ).save()

    def reject(self, completed_by, reason, notify=False):
        self.status = 'rejected'
        self.completed_by = completed_by
        self.reject_reason = reason
        self.save()
        if notify:
            notification.send([self.author], 'crm_reassignrequest_rejected', {'obj': self})


class NotificationObjectManager(models.Manager):
    pass


class Notification(models.Model):
    """Special user-nitification for CRM events and tasks. Works like simple queue."""
    NOTIFY_TYPES = (
        ('client_call', u"Звонок клиента"),
        ('new_client', u"Новый клиент"),
        ('message', u"Сообщение"),
    )
    type = models.CharField(u'Тип', choices=NOTIFY_TYPES, default='message', max_length=255)
    user = models.ForeignKey(User, verbose_name=u"Пользователь", related_name='+')
    created_at = models.DateTimeField(u"Дата создания", auto_now_add=True, null=True)
    sent_at = models.DateTimeField(u"Дата отправки", null=True)
    is_sent = models.BooleanField(u"Отправлена", default=False)
    text = models.TextField(u"Текст")
    params = JSONField(u"Дополнительные параметры", default={})

    objects = NotificationObjectManager()

import os.path

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from geobase.models import Country, Region
from node.models import Node
from settings import STATIC_ROOT, PARTNER_SUPPORT_EMAIL
from shared.utils import upload_to
from shared.validators import email_re


class RegionalOfficeObjectManager(models.QuerySet):
    our = lambda self: self.filter(is_our=True)
    not_our = lambda self: self.filter(is_our=False)

    def crm_managers(self):
        from crm.models import PersonalManager
        return PersonalManager.objects.filter(office__in=self)

    def by_agent_code(self, agent_code):
        return self.filter(id__in=[
            ro.id for ro in self
            if agent_code in ro.get_agent_codes()])

    def with_agent_codes(self):
        return self.exclude(Q(agent_codes=None) | Q(agent_codes=""))

    def get_agent_codes(self):
        offices = self.with_agent_codes().values_list('agent_codes', flat=True)
        return sum([
            map(int, o.split(','))
            for o in offices
        ], [])


class RegionalOffice(models.Model):
    """Региональный офис"""
    is_active = models.BooleanField(u"Офис активен", default=True)
    slug = models.SlugField(u'Слаг', help_text=u'Машинное имя, для ссылок')
    name = models.CharField(u'Город', max_length=50)
    caption = models.CharField(u'Заголовок', max_length=150, null=True, blank=True)
    description = models.TextField(u'Описание', null=True, blank=True)
    address = models.TextField(u'Адрес', null=True)
    metro = models.CharField(u"Метро", help_text=u"Если в городе нет метро - оставьте пустым",
                             max_length=255, null=True, blank=True)
    email = models.EmailField(verbose_name=u'E-mail офиса (основной)', null=True, blank=True)
    _phones = models.TextField(u'Телефоны офиса', help_text=u"Каждый теелфон на новой строке",
                               max_length=1024, blank=True)
    agent_codes = models.CommaSeparatedIntegerField(u'Партнерские номера', max_length=1024, null=True, blank=True,
                                                    help_text=u'Через запятую, без пробелов')
    country = models.ForeignKey(Country, verbose_name=u"Страна", related_name='regional_offices')
    state = models.ForeignKey(Region, verbose_name=u"Штат/Регион", blank=True, null=True,
                              related_name="regional_offices")
    can_deposit_or_withdraw = models.BooleanField(u"Может совершать ввод/вывод наличными", default=False)
    emails = models.CharField(u"Email'ы, на которые слать запросы на обучение",
                              default=PARTNER_SUPPORT_EMAIL['default'],
                              max_length=255,
                              help_text=u'через запятую')
    hidden = models.BooleanField(u"Только контакты", default=False,
                                 help_text=u"Если отмечено, офис будет только показываться в списке")
    is_our = models.BooleanField(u"Наш филиал", default=False,
                                 help_text=u"Если не отмечено, клиенты офиса не будут крепиться к нашим менеджерам")

    # yandex explicit coords
    yd_map_x = models.FloatField(u"X координата YandexMaps", null=True, blank=True)
    yd_map_y = models.FloatField(u"Y координата YandexMaps", null=True, blank=True)

    # 41.766765,44.787877

    objects = RegionalOfficeObjectManager.as_manager()

    def __unicode__(self):
        return self.name

    @property
    def agent_code(self):
        if self.agent_codes:
            return int(self.agent_codes.split(',')[0])

    def get_agent_codes(self):
        return map(int, self.agent_codes.split(',')) if self.agent_codes else []

    def get_absolute_url(self):
        return reverse('about_regional_office', args=[self.slug])

    def get_valid_emails(self):
        return [email for email in self.emails.split(',') if email_re.match(email)]

    def get_img_path(self):
        return os.path.join(STATIC_ROOT, 'img/regions', self.slug + '.jpg')

    def head_managers(self):
        from crm.models import PersonalManager
        return PersonalManager.objects.filter(office=self, is_office_supermanager=True, user__is_active=True)

    @property
    def phones(self):
        return [p.strip() for p in self._phones.split('\n')]

    @property
    def phone(self):
        phones = self.phones
        return phones[0] if phones else None

    class Meta:
        ordering = ['name']
        verbose_name = u'Региональный офис'
        verbose_name_plural = u'Региональные офисы'


@receiver(post_migrate)
def create_permissions(sender, **kwargs):
    if sender.label != 'regions':
        return
    for region in RegionalOffice.objects.all():

        permission, created = Permission.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(RegionalOffice),
            codename="can_edit_%s" % region.slug)

        if created:
            permission.name = "Can edit region %s" % region.name.lower()
            permission.save()
            print "Adding permission: %s" % permission
