# -*- coding: utf-8 -*-
from datetime import *
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from contextlib import contextmanager
from .middleware import get_current_request


class Event(object):
    @classmethod
    def all(cls):
        items = map(lambda name: getattr(cls, name), dir(cls))
        return [
            item
            for item in items
            if isinstance(item, Event)]

    def __init__(self, slug, label=None):
        self.slug = slug
        self.label = label

    def log(self, content_object=None, params=None, **kwargs):
        return Logger.log(
            event=self.slug, content_object=content_object, params=params, **kwargs)

    @property
    def qs(self):
        return Logger.objects.filter(event=self.slug)

# Аккаунт и профиль:

Event.LOGIN_OK = Event("login ok", _(u"Удачный логин"))
Event.LOGIN_FAIL = Event("login fail", _(u"Неудачный логин"))
Event.PASSWORD_RESTORED = Event("password restored", _(u"Восстановление пароля"))
Event.PASSWORD_CHANGE_OK = Event("password changed ok", _(u"Удачная смена пароля"))
Event.PASSWORD_CHANGE_FAIL = Event("password changed fail", _(u"Неуд. смена пароля"))
Event.PROFILE_CHANGED = Event("profile changed", _(u"Изменение профиля"))
Event.PROFILE_SAVED = Event("profile saved", _(u"Сохранение профиля"))
Event.USER_SAVED = Event("user saved", _(u"Сохранение юзера"))
Event.VALIDATION_OK = Event("validation ok", _(u"Валидация профиля"))
Event.VALIDATION_REVOKED = Event("validation revoked", _(u"Снятие валидации"))
Event.PHONE_VALIDATION_BY_USER = Event("user validation", _(u"Валидация телефона"))
Event.DOCUMENT_UPLOADED = Event("document uploaded", _(u"Загружен документ"))
Event.MANAGER_CHANGED = Event("manager changed", _(u"Менеджер изменён"))
Event.IB_MANAGER_CHANGED = Event("ib manager changed", _(u"IB-Менеджер изменён"))
Event.MANAGER_REASSIGN_REQUEST_ACCEPTED = Event("manager reassign request accepted", _(u"Запрос на смену менеджера одобрен"))
Event.HAS_BEEN_TAKEN_BY_MANAGER = Event("has been taken by manager", _(u"Был взят менеджером"))

# OTP

Event.OTP_LOGIN_OK = Event("otp login ok", _(u"Удачный OTP логин"))
Event.OTP_LOGIN_FAIL = Event("otp login fail", _(u"Неудачный OTP логин"))
Event.OTP_OK = Event("otp auth ok", _(u"Удачная OTP аутентиф."))
Event.OTP_FAIL = Event("otp auth fail", _(u"Неудачная OTP аутентиф."))
Event.OTP_BINDING_CREATED = Event("otp binding created", _(u"Создание OTP"))
Event.OTP_IS_LOST = Event("otp is lost", _(u"OTP потерян"))


# Счета:

Event.ACCOUNT_CREATED = Event("account created", _(u"Создание счета"))
Event.ACCOUNT_DELETED = Event("account deleted", _(u"Удаление счета"))
Event.ACCOUNT_PASSWORD_RESTORED = Event("account password restored", _(u"Восст. пароля от счета"))
Event.LEVERAGE_CHANGED = Event("leverage changed", _(u"Смена плеча"))
Event.OPTIONS_STYLE_CHANGED = Event("options style changed", _(u"Сменя стиля опционов"))
Event.REBATE_CHANGED = Event("rebate changed", _(u"Изменён возврат спреда"))
Event.WEBTRADER_LOGIN = Event("webtrader login", _(u"Логин в веб-трейдер"))
Event.ACCOUNT_BLOCK = Event("account block", _(u"Счет заблокирован"))
Event.ACCOUNT_UNBLOCK = Event("account block", _(u"Счет разблокирован"))

# Ввод/вывод:

Event.REQUISIT_CREATED = Event("requisit created", _(u"Создание реквизита"))
Event.REQUISIT_CHANGED = Event("requisit changed", _(u"Изменение реквизита"))
Event.REQUISIT_VALIDATION_UPDATE = Event("requisit validation update", _(u"Обновление валидации"))  # catches on_post_save
Event.REQUISIT_DELETED = Event("requisit deleted", _(u"Удаление реквизита"))
Event.DEPOSIT_REQUEST_CREATED = Event("deposit request created", _(u"Созд. заявки на ввод"))
Event.WITHDRAW_REQUEST_CREATED = Event("withdraw request created", _(u"Созд. заявки на вывод"))
Event.INTERNAL_TRANSFER = Event("internal transfer", _(u"Внутренний перевод"))
Event.EDUCATION_PAYMENT = Event("education payment", _(u"Оплата обучения"))
Event.CONSULTATION_PAYMENT = Event("consultation payment", _(u"Оплата консультации"))


# Памм:

Event.PAMM_STATUS_UPDATE = Event("pamm status update", _(u"Обн. статуса счета"))
Event.REPLICATION_RATIO_CHANGED = Event("replication ratio changed", _(u"Изм. коэфф. копир."))
Event.NOTIFICATION_RATIO_CHANGED = Event("notification ratio changed", _(u"Изм. коэфф. уведомл."))
Event.MINIMAL_EQUITY_CHANGED = Event("minimal equity changed", _(u"Изменение порога откл."))
Event.MAX_LOSSES_REACHED = Event("max loss reached", _(u"Сраб. порога откл."))

# VPS:

Event.VPS_SUBSCRIPTION = Event("vps subscription", _(u"Подписка GC VPS"))
Event.VPS_SUBSCRIPTION_EXTENDED = Event("vps subscription extended", _(u"Продление GC VPS"))

# CRM:

Event.ACCOUNT_DATA_VIEW_EXCEEDED = Event("account data view exceeded", _(u"Превышен лимит на просмотр данных пользователей"))

# WITHDRAW REQUESTS GROUP
Event.WITHDRAW_REQUESTS_GROUP_CREATED = Event("withdraw requests group created", _(u"Группа заявок на вывод создана"))
Event.WITHDRAW_REQUESTS_GROUP_CLOSED = Event("withdraw requests group closed", _(u"Группа заявок на вывод закрыта"))

# WITHDRAW REQUESTS GROUP APPROVAL
Event.WITHDRAW_REQUESTS_GROUP_APPROVAL_RESULT_CHANGED = Event("withdraw requests group approval changed", _(u"Группа заявок на вывод: одобрение изменено"))
Event.WITHDRAW_REQUESTS_GROUP_APPROVAL_RESET = Event("withdraw requests group approval reset", _(u"Группа заявок на вывод: одобрение снято"))

# WITHDRAW REQUEST
Event.WITHDRAW_REQUEST_FAILED = Event("withdraw requests failed", _(u"Заявка на вывод: неудачное снятие"))
Event.WITHDRAW_REQUEST_FAST_DECLINED = Event("withdraw request fast declined", _(u"Заявка на вывод: заявка отклонена"))
Event.WITHDRAW_REQUEST_WEBMONEY_PLUGIN_PAYED = Event("withdraw requests webmoney plugin payed", _(u"Заявка на вывод: выплата через плагин"))
Event.WITHDRAW_REQUEST_PAYED = Event("withdraw requests payed", _(u"Заявка на вывод: успешное снятие средств"))
Event.WITHDRAW_REQUEST_READY_FOR_PAYMENT = Event("withdraw request ready for payment", _(u"Заявка на вывод готова к выплате"))
Event.WITHDRAW_REQUEST_READY_FOR_PAYMENT_RESET = Event("withdraw request ready for payment reset", _(u"Заявка на вывод не готова к выплате"))
Event.WITHDRAW_REQUEST_COMMITTED = Event("withdraw request committed", _(u"Заявка на вывод: выплачено"))

# GCRM LOGS
Event.GCRM_CONTACT_CREATED = Event("gcrm contact created", _(u"Контакт создан"))
Event.GCRM_MANAGER_CHANGED = Event("gcrm manager changed", _(u"Менеджер изменён"))
Event.GCRM_MANAGER_CHANGED_BY_REQUEST = Event("gcrm manager changed by request", _(u"Менеджер изменён по запросу"))
Event.GCRM_MANAGER_CHANGED_BY_BUTTON = Event("gcrm manager changed by button", _(u"Контакт взят менеджером"))
Event.GCRM_MANAGER_SET_NEW_PASSWORD = Event("gcrm manager set new password", _(u"Менеджеру изменен пароль"))
Event.GCRM_MANAGER_RENAME = Event("gcrm manager rename", _(u"Менеджеру изменено имя"))
Event.GCRM_MANAGER_REVOKE = Event("gcrm manager revoke", _(u"Менеджер удален"))
Event.GCRM_NEW_MANAGER_MANUALLY = Event("gcrm new manager manually", _(u"Добавлен новый менеджер вручную"))


class Events(object):

    # Аккаунт и профиль:

    LOGIN_OK = "login ok"
    LOGIN_FAIL = "login fail"
    PASSWORD_RESTORED = "password restored"
    PASSWORD_CHANGE_OK = "password changed ok"
    PASSWORD_CHANGE_FAIL = "password changed fail"
    PROFILE_CHANGED = "profile changed"
    PROFILE_SAVED = "profile saved"
    USER_SAVED = "user saved"
    VALIDATION_OK = "validation ok"
    VALIDATION_REVOKED = "validation revoked"
    PHONE_VALIDATION_BY_USER = "user validation"
    DOCUMENT_UPLOADED = "document uploaded"
    MANAGER_CHANGED = "manager changed"
    IB_MANAGER_CHANGED = "ib manager changed"
    MANAGER_REASSIGN_REQUEST_ACCEPTED = "manager reassign request accepted"

    # OTP

    OTP_LOGIN_OK = "otp login ok"
    OTP_LOGIN_FAIL = "otp login fail"
    OTP_OK = "otp auth ok"
    OTP_FAIL = "otp auth fail"
    OTP_BINDING_CREATED = "otp binding created"

    # Счета:

    ACCOUNT_CREATED = "account created"
    ACCOUNT_DELETED = "account deleted"
    ACCOUNT_PASSWORD_RESTORED = "account password restored"
    LEVERAGE_CHANGED = "leverage changed"
    OPTIONS_STYLE_CHANGED = "options style changed"
    WEBTRADER_LOGIN = "webtrader login"

    # Ввод/вывод:

    REQUISIT_CREATED = "requisit created"
    REQUISIT_CHANGED = "requisit changed"
    REQUISIT_VALIDATION_UPDATE = "requisit validation update"  # catches on_post_save
    REQUISIT_DELETED = "requisit deleted"
    DEPOSIT_REQUEST_CREATED = "deposit request created"
    WITHDRAW_REQUEST_CREATED = "withdraw request created"
    INTERNAL_TRANSFER = "internal transfer"
    EDUCATION_PAYMENT = "education payment"
    CONSULTATION_PAYMENT = "consultation payment"

    # Памм:

    PAMM_STATUS_UPDATE = "pamm status update"
    REPLICATION_RATIO_CHANGED = "replication ratio changed"
    NOTIFICATION_RATIO_CHANGED = "notification ratio changed"
    MINIMAL_EQUITY_CHANGED = "minimal equity changed"
    MAX_LOSSES_REACHED = "max loss reached"

    # VPS:

    VPS_SUBSCRIPTION = "vps subscription"
    VPS_SUBSCRIPTION_EXTENDED = "vps subscription extended"

    # CRM:

    ACCOUNT_DATA_VIEW_EXCEEDED = "account data view exceeded"

    # WITHDRAW REQUESTS GROUP
    WITHDRAW_REQUESTS_GROUP_CREATED = "withdraw requests group created"
    WITHDRAW_REQUESTS_GROUP_CLOSED = "withdraw requests group closed"

    # WITHDRAW REQUESTS GROUP APPROVAL
    WITHDRAW_REQUESTS_GROUP_APPROVAL_RESULT_CHANGED = "withdraw requests group approval changed"
    WITHDRAW_REQUESTS_GROUP_APPROVAL_RESET = "withdraw requests group approval reset"

    # WITHDRAW REQUEST
    WITHDRAW_REQUEST_FAILED = "withdraw requests failed"
    WITHDRAW_REQUEST_FAST_DECLINED = "withdraw request fast declined"
    WITHDRAW_REQUEST_WEBMONEY_PLUGIN_PAYED = "withdraw requests webmoney plugin payed"
    WITHDRAW_REQUEST_PAYED = "withdraw requests payed"
    WITHDRAW_REQUEST_READY_FOR_PAYMENT = "withdraw request ready for payment"
    WITHDRAW_REQUEST_READY_FOR_PAYMENT_RESET = "withdraw request ready for payment reset"
    WITHDRAW_REQUEST_COMMITTED = "withdraw request committed"


class LoggerQuerySet(models.QuerySet):
    def by_object(self, object):
        return self.filter(
            object_id=object.pk,
            content_type=ContentType.objects.get_for_model(type(object))
        )

    def by_object_ids(self, model, ids):
        return self.filter(
            object_pk__in=set(ids),
            content_type=ContentType.objects.get_for_model(model)
        )

    def by_user(self, user):
        return self.filter(user=user)

    def prefetch_params(self):
        class LoggerProxyQueryset(object):
            def __init__(self, qs):
                self.qs = qs

            def __getitem__(self, item):
                self.qs = self.qs.__getitem__(item)
                return self

            def __getattr__(self, name):
                if name not in ['all', 'filter', 'exclude', 'order_by', 'select_related', 'prefetch_related']:
                    return getattr(self.qs, name)

                method = getattr(self.qs, name)

                def wrapper(*a, **kwa):
                    self.qs = method(*a, **kwa)
                    return self
                return wrapper

            def __iter__(self):
                objects = list(self.qs.prefetch_related('content_object'))

                # collect users ids to fetch in one query
                users_ids = set()
                for log in objects:
                    for k, v in log.params.iteritems():
                        if k.endswith('_user_id'):
                            users_ids.add(v)
                    # optimize select/prefetch related too
                    if log.user_id:
                        users_ids.add(log.user_id)

                # query it
                users = {
                    u.pk: u
                    for u in User.objects.filter(pk__in=users_ids)
                        .select_related('profile', 'crm_manager', 'crm_manager__office')
                }
                users[None] = None

                # pack it back
                for log in objects:
                    for k, v in log.params.items():
                        if k.endswith('_user_id'):
                            del log.params[k]
                            log.params[k.split('_user_id')[0]] = users[v]
                    if log.user_id:
                        log.user = users[log.user_id]
                return iter(objects)
        return LoggerProxyQueryset(self)

        # # collect users ids to fetch in one query
        # users_ids = set()
        # for log in self:
        #     for k, v in log.params.iteritems():
        #         if k.endswith('_user_id'):
        #             users_ids.add(v)
        #     # optimize select/prefetch related too
        #     if log.user_id:
        #         users_ids.add(log.user_id)
        #
        # # query it
        # users = {u.pk: u for u in User.objects.filter(pk__in=users_ids)}
        # users[None] = None
        #
        # # pack it back
        # logs = []
        # for log in self:
        #     for k, v in log.params.items():
        #         if k.endswith('_user_id'):
        #             del log.params[k]
        #             log.params[k.split('_user_id')[0]] = users[v]
        #     if log.user_id:
        #         log.user = users[log.user_id]
        #     logs.append(log)
        # return logs


class Logger(models.Model):
    ip = models.IPAddressField(_("User IP"), null=True, blank=True)
    user = models.ForeignKey(User, verbose_name=_("User"), related_name="log", null=True, blank=True, db_index=True)
    at = models.DateTimeField(_("Time of change"), auto_now_add=True, db_index=True)
    params = JSONField(_("Additional parameters"), default={})

    object_id = models.PositiveIntegerField(null=True, db_index=True)
    content_type = models.ForeignKey(ContentType, null=True, db_index=True)
    content_object = generic.GenericForeignKey()

    event = models.CharField(_("Type of action"), max_length=50, choices=[
        (event.slug, event.label)
        for event in Event.all()
    ], db_index=True)

    objects = LoggerQuerySet.as_manager()

    class Meta:
        verbose_name = _(u"запись лога")
        verbose_name_plural = _(u"записи лога")

    def __repr__(self):
        return " - ".join(map(str, [self.user if self.user else "anon", self.event,
                                    self.content_object, self.params, self.at]))

    @classmethod
    def log(cls, event, content_object=None, params=None, at=None, ip=None, user=None, save=True):
        at = at or datetime.now()
        request = get_current_request()
        if request:
            ip = ip or request.META["REMOTE_ADDR"]
            user = user or (request.user if request.user.is_authenticated() else None)
        log = Logger(
            event=event, content_object=content_object, params=params or {},
            at=at, ip=ip, user=user)

        if cls.tags_stack:
            log.params['tags'] = cls.tags_stack
        for d in cls.params_stack:
            log.params.update(d)
        if save:
            log.save()
        return log

    @classmethod
    @contextmanager
    def with_tag(cls, tag):
        cls.tags_stack.append(tag)
        try:
            yield
        finally:
            cls.tags_stack.pop()
    tags_stack = []

    @classmethod
    @contextmanager
    def with_params(cls, **params):
        cls.params_stack.append(params)
        try:
            yield
        finally:
            cls.params_stack.pop()
    params_stack = []
