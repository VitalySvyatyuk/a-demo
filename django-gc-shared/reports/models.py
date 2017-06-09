# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

import platforms.types, platforms.models


class Report(models.Model):
    """A dummy report model.

    We need it because __all__ Django Permissions should be related to
    some Model, and since we need instance-based permissions we cheat
    the system, by creating all the permissions manually on post_syncdb,
    for each of the reports listed in settings.REPORTS (see __init__.py).
    """


class AccountGroupManager(models.Manager):
    def for_user(self, user):
        # если есть разрешение reports.can_use_any_account, то показываются все группы
        if user.has_perm("reports.can_use_any_account"):
            return self.get_queryset().all()
        # если есть разрешение reports.can_use_account_groups, то в групповых отчетах
        # можно использовать только те группы, в которых состоит пользователь
        elif user.has_perm("reports.can_use_account_groups"):
            return self.get_queryset().filter(allowed_users=user)
        # в остальных случаях пользователь никакие группы использовать не может
        else:
            return self.get_empty_query_set()

    def excluded_for_user(self, user):
        return self.get_queryset().filter(force_exclude_for_users=user)


class AccountGroup(models.Model):
    name = models.CharField(max_length=50)
    _account_mt4_ids = models.TextField(help_text="One Mt4_Id on a line", blank=True)
    query = models.TextField(u'Eval-запрос', null=True, blank=True,
                             help_text=u'Должен вернуть список логинов mt4')
    slug = models.SlugField(_('Slug'), blank=True, null=True, editable=False)
    subpartner_user = models.ForeignKey(User, blank=True, null=True, verbose_name="Partner's manager")
    allowed_users = models.ManyToManyField(
        User, blank=True,
        related_name="allowed_account_groups",
        help_text=u"Пользователь может запрашивать отчёты для этой группы счетов (при наличии соответствующих прав)",
        limit_choices_to={'user_permissions__codename': "can_use_account_groups",
                          'user_permissions__content_type__app_label': "reports"})
    force_exclude_for_users = models.ManyToManyField(
        User, blank=True,
        related_name="excluded_account_groups",
        help_text=u"Эта группа обязательно исключается при запросе отчётов этими пользователями",
        limit_choices_to=(Q(user_permissions__codename="can_use_account_groups") |
                          Q(user_permissions__codename="can_use_any_account")) &
                          Q(user_permissions__content_type__app_label="reports")
    )
    does_not_need_manager = models.BooleanField(
        u"Не нужен менеджер", default=False,
        help_text=u"Клиентам, открывшимся под этими партнёрскими счётами, не требуется "
                  u"персональный менеджер (например, если это рег. офисы)")

    objects = AccountGroupManager()

    @property
    def account_mt4_ids(self):
        return list(set([id.strip() for id in self._account_mt4_ids.splitlines() if id.strip().isdigit()]
                        + self._eval_query()))

    @property
    def account_count(self):
        return len(self.account_mt4_ids)

    def _eval_query(self):
        """Evaluate the query"""
        import datetime

        if not self.query:
            return []

        mt4_ids = eval(self.query, {}, {'User': User, 'datetime': datetime, 'Q': models.Q,
                                        'account_types': platforms.types, 'mt4_models': platforms.models})
        return list(set(mt4_ids))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Account group')
        verbose_name_plural = _('Account groups')


class SavedReport(models.Model):
    for_user = models.ForeignKey(User, related_name="saved_reports")
    name = models.TextField()
    filename = models.CharField(max_length=100, null=True, blank=True)
    celery_task_id = models.CharField(max_length=100, null=True, blank=True)
    creation_ts = models.DateTimeField(auto_now_add=True)

    @property
    def view_link(self):
        return reverse('reports_view_report', args=(self.pk,))

    @property
    def is_ready(self):
        return bool(self.filename)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Saved report')
        verbose_name_plural = _('Saved reports')


class SavedReportData(models.Model):
    data = JSONField(u"Результат", default={})
    params = JSONField(u"Параметры", default={}, help_text=u"Параметры использовавшиеся для запроса отчёта")
    creation_ts = models.DateTimeField(auto_now_add=True)

    def run_report(self):
        if self.pk:
            raise ValueError("This report has already been generated")

        # TODO: do the job
        self.data = None
        self.save()


class IBSettings(models.Model):
    REWARD_TYPES = (
        (0, u"Менеджер"),
        (1, u"Собственный офис"),
        (2, u"CL"),
        (3, u"Ручное начисление"),
    )

    ib_account = models.PositiveIntegerField(u"№ партнёрского счёта", primary_key=True)
    reward_type = models.PositiveSmallIntegerField(u"Тип вознаграждения", choices=REWARD_TYPES)
    cl_percent = models.PositiveSmallIntegerField(u"%CL", blank=True, null=True)
