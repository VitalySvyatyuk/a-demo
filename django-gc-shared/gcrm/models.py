# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from datetime import datetime, time, timedelta
from django.db import models
from django.db.models import Value, F, Func
from django.core.exceptions import MultipleObjectsReturned
from django.db.models.functions import Concat
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.dispatch import receiver

from registration.signals import user_registered
from .utils import user_can_manage
from annoying.fields import JSONField
from gcrm.utils import StatefullModel
from django.db import transaction
from log.models import Event, Logger
from shared.werkzeug_utils import cached_property

@cached_property
def is_gcrm_manager(self):
    # load full object since on successful check,
    # we probably will need it anyway
    try:
        return bool(self.crm_manager)
    except:
        return False
    return False
User.is_gcrm_manager = is_gcrm_manager


class ContactQuerySet(models.QuerySet):
    @transaction.atomic
    def set_manager(self, user, update_profile=True, event=Event.GCRM_MANAGER_CHANGED, comment=None, additional_info=None):
        data = list(self.exclude(manager=user).values_list('id', 'manager'))  # for logging

        # remove tasks since no one be able to complete it
        # and if task really needs to be completed, it will be recreated by other logic
        if not user:
            Task.objects.filter(contact__in=self, assignee=F('contact__manager'), closed_at=None).delete()

        # with certain manager, move tasks to new manager
        else:
            Task.objects.filter(
                contact__in=self, assignee=F('contact__manager'), closed_at=None
            ).update(assignee=user)

        # move expired tasks
        Task.objects.filter(
            contact=self, assignee=user, deadline__lte=datetime.now()
        ).update(deadline=datetime.now()+timedelta(days=7))

        # set manager
        self.exclude(manager=user).update(
            manager=user, assigned_ts=datetime.now(), is_assigned_by_button=False
        )

        # backward compat
        if update_profile:
            from profiles.models import UserProfile
            UserProfile.objects.filter(user__gcrm_contact__in=self).update(manager=user)

        # log it
        params = dict(
            new_user_id=user.pk if user else None,
            **(additional_info or {})
        )

        if comment:
            params['comment'] = comment
        Logger.objects.bulk_create([
            event.log(Contact(pk=id, id=id), dict(old_user_id=man, **params), save=False) for id, man in data
        ])


class Contact(StatefullModel):
    objects = ContactQuerySet.as_manager()
    user = models.OneToOneField(User, related_name='gcrm_contact', blank=True, null=True)

    name = models.CharField('Имя', max_length=1024)
    name_sync_from_user = models.BooleanField('Использовать имя из пользователя', default=False)

    manager = models.ForeignKey(User, related_name='gcrm_contacts', blank=True, null=True)
    assigned_ts = models.DateTimeField('Дата установки менеджера', null=True)
    is_assigned_by_button = models.BooleanField('Взят по кнопке', default=False)

    # info is a list of dicts, e.g. [{"type": "email", "value": "mail@example.com"}]
    # possible types are: email, phone, address
    info = JSONField('Контактная информация', default=list)
    tags = ArrayField(models.CharField(max_length=255), verbose_name='Тэги', default=list)
    system_tags = ArrayField(models.CharField(max_length=255), verbose_name='Системные тэги', default=list)

    # last_non_completed_task = models.ForeignKey('Task', related_name='+', blank=True, null=True)

    search_cache = models.TextField('Кеш поиска', default='')

    update_ts = models.DateTimeField('Дата изменения', auto_now=True)
    creation_ts = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        permissions = (
            ("user_reset_otp", "Can reset OTP of observable contacts"),
        )

    def __str__(self):
        return '%s' % (self.user)

    @classmethod
    def append_search_cache(cls, user, data):
        if not data:
            return
        Contact.objects.filter(user=user).exclude(search_cache__icontains=data).update(
            search_cache=Concat(F('search_cache'), Value(";"), Value(data))
        )

    @classmethod
    def append_system_tags(cls, user, tags):
        for tag in tags:
            if tag:
                tag = unicode(tag)
                Contact.objects.filter(user=user).exclude(system_tags__contains=[tag]).update(
                    system_tags=Func(F('system_tags'), Value(tag), function='array_append')
                )

    def add_task(self, type='CALL', text='Call ASAP', at=None, assignee=None, force_time=None, get_or_create=True, notify=True):
        if not assignee:
            assignee = self.manager
        if not (assignee and hasattr(assignee, 'crm_manager')):
            return None, False

        if assignee.crm_manager.force_tasks_full_day:
            force_time = time(23, 59, 59)

        from crm.utils import calculate_finish_time
        deadline = calculate_finish_time(assignee, at=at, force_time=force_time)

        method = Task.objects.get_or_create if get_or_create else (lambda **kwa: (Task.objects.create(**kwa), True))
        try:
            task, created = method(contact=self, task_type=type, text=text, deadline=deadline, assignee=assignee)
        # get_or_create 4 sure
        except MultipleObjectsReturned:
            task, created = None, False
        if created and notify:
            task.send_creation_notification()
        return task, created

    def add_note(self, text, get_or_create=False):
        method = Note.objects.get_or_create if get_or_create else Note.objects.create
        return method(contact=self, text=text)


    @property
    def calls(self):
        from telephony.models import CallDetailRecord
        qss = []
        for info in self.info:
            if info['type'] == 'phone':
                qss.append(CallDetailRecord.objects.by_number(info['value']))
        if self.user:
            qss.append(CallDetailRecord.objects.by_user(self.user))
        return reduce(lambda x, y: x | y, qss) if qss else CallDetailRecord.objects.none()

    def get_absolute_url(self):
        return "/gcrm/contact/%d" % self.pk

    def slug_tag(self):
        return u', '.join(self.tags)
    slug_tag.allow_tags = True
    slug_tag.short_description = "Tags"

    @property
    def logs(self):
        from log.models import Logger
        return Logger.objects.by_object(self)

    @property
    def related_logs(self):
        return self.user.profile.related_logs | self.logs

    def set_manager(self, *a, **kwa):
        """
        Method to change manager with default log message
        If you have special log event type, avoid this method
        In nutshell, it has no magic, just a shortcut
        """
        return Contact.objects.filter(pk=self.pk).set_manager(*a, **kwa)


@receiver(user_registered)
def create_contact_for_new_user(sender, **kwargs):
    user = kwargs['user']
    profile = user.profile
    Contact.objects.get_or_create(name=profile.get_full_name(), user=user,
                                  info=[{"type": "phone", "value": profile.phone_mobile or profile.phone_work or profile.phone_home},
                                        {"type": "email", "value": user.email}])


class Note(StatefullModel):
    legacy_id = models.IntegerField(null=True, blank=True)
    contact = models.ForeignKey(Contact, related_name='notes')
    author = models.ForeignKey(User, related_name='+', null=True)
    text = models.TextField('Текст')
    update_ts = models.DateTimeField('Дата изменения', auto_now=True)
    creation_ts = models.DateTimeField('Дата создания', auto_now_add=True)

    def is_editable_by(self, user):
        return (
            # allow to edit by author in 10 minutes
            (user == self.author and (datetime.now() - self.creation_ts).seconds < 10*60)
            # supermanagers
            or user_can_manage(user, self.author, self=False))


class TaskQuerySet(models.QuerySet):
    def overdue(self):
        return self.filter(closed_at=None, deadline__lt=datetime.now())


class Task(StatefullModel):
    objects = TaskQuerySet.as_manager()
    legacy_id = models.IntegerField(null=True, blank=True)
    contact = models.ForeignKey(Contact, related_name='tasks')
    author = models.ForeignKey(User, related_name='+', null=True)

    text = models.TextField('Текст')

    update_ts = models.DateTimeField('Дата изменения', auto_now=True)
    creation_ts = models.DateTimeField('Дата создания', auto_now_add=True)

    TASK_TYPES = (
        ('CALL', 'Звонок'),
        ('LETTER', 'Письмо'),
        ('MEETING', 'Встреча'),
        ('MONITORING', 'Мониторинг'),
        ('LECTURE', 'Лекция'),
        ('PRACTICE', 'Практика')
    )

    task_type = models.CharField('Тип', choices=TASK_TYPES, default='CALL', max_length=255)

    assignee = models.ForeignKey(User, related_name='assigned_crm_tasks')
    deadline = models.DateTimeField('Дедлайн')

    closed_at = models.DateTimeField('Дата закрытия', null=True, blank=True)
    close_comment = models.TextField('Комментарий к закрытию', null=True, blank=True)

    @property
    def is_completed(self):
        return bool(self.closed_at)

    @property
    def is_expired(self):
        return (self.closed_at if self.is_completed else datetime.now()) > self.deadline

    def is_completable_by(self, user):
        return not self.is_completed and user_can_manage(user, self.assignee)

    def is_editable_by(self, user):
        return not self.is_completed and (
            # allow to edit by author in 10 minutes
            (user == self.author and (datetime.now() - self.creation_ts).seconds < 10*60)
            # supermanagers
            or user_can_manage(user, self.author, self=False))

    def send_creation_notification(self):
        from django.template.loader import render_to_string
        html_content = render_to_string('gcrm/emails/new_task.html', {
            'object': self
        })
        self.assignee.email_user(
            'GCRM Task: {}'.format(self.text), '-',
            from_email="security@grandcapital.net",
            html_message=html_content
        )


class ManagerReassignRequestQuerySet(models.QuerySet):
    def unresolved(self):
        return self.filter(result=None)


class ManagerReassignRequest(StatefullModel):
    objects = ManagerReassignRequestQuerySet.as_manager()
    contact = models.ForeignKey(Contact, related_name='manager_reassign_requests')
    author = models.ForeignKey(User, related_name='+')
    comment = models.TextField('Комментарий', default='')
    new_manager = models.ForeignKey(User, related_name='+', null=True)
    previous_manager = models.ForeignKey(User, related_name='+', null=True)

    result = models.NullBooleanField('Результат', default=None)
    closed_by = models.ForeignKey(User, related_name='+', null=True)
    close_comment = models.TextField('Комментарий к решению', null=True)

    update_ts = models.DateTimeField('Дата изменения', auto_now=True)
    creation_ts = models.DateTimeField('Дата создания', auto_now_add=True)

    with_task = models.TextField('Назначить новому менеджеру задачу при одобрении', blank=True)

    def accept(self, closed_by, close_comment=None, child=False):
        self.close_comment = close_comment or ''
        self.closed_by = closed_by
        self.result = True
        self.save()

        if not child:
            self.contact.set_manager(self.new_manager, comment=self.comment, additional_info={'request_id': self.pk})
            for req in self.contact.manager_reassign_requests.unresolved().filter(new_manager=self.new_manager):
                req.accept(closed_by, close_comment, child=True)

        if self.with_task:
            task = Task(contact=self.contact,
                        author=self.author,
                        text=self.with_task,
                        assignee=self.new_manager,
                        deadline=datetime.now().replace(hour=23, minute=59, second=59))
            task.save()

    def is_editable_by(self, user):
        return self.result is None and user_can_manage(user, self.new_manager) and user_can_manage(user, self.previous_manager)


class ContactUserViewRecord(StatefullModel):
    contact = models.ForeignKey(Contact, related_name='+')
    user = models.ForeignKey(User, related_name='+')
    creation_ts = models.DateTimeField('Дата создания', auto_now_add=True)


from gcrm.signal_handlers import *
