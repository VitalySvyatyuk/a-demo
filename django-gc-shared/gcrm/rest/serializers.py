# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from crm.models import PersonalManager
from currencies.rest_fields import MoneyField
from gcrm.models import Contact, ManagerReassignRequest, Task, Note
from gcrm.utils import user_can_manage
from geobase.models import Country
from geobase.models import Region
from log.models import Event, Logger
from platforms.models import TradingAccount
from payments.models import DepositRequest, WithdrawRequest
from project.rest_fields import JSONSerializerField
from crm.models import RegionalOffice
from reports.models import AccountGroup
from telephony.models import CallDetailRecord
from platforms.exceptions import PlatformError
from currencies.money import NoneMoney

from logging import getLogger
log = getLogger(__name__)

class ManagerReassignRequestSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    editable = serializers.SerializerMethodField()

    def get_contact(self, obj):
        data = {
            'id': obj.contact_id
        }
        if 'view' in self.context:
            data.update({
                'name': obj.contact.user.profile.get_full_name() if obj.contact.user else obj.contact.name,
            })
        return data

    def get_editable(self, obj):
        return obj.is_editable_by(self.context['request'].user)

    class Meta:
        model = ManagerReassignRequest


class RejectReassignRequestSerializer(serializers.ModelSerializer):
    close_comment = serializers.CharField()

    class Meta:
        model = ManagerReassignRequest
        fields = ('close_comment',)


class AccountSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    group_slug = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()

    def get_group_slug(self, obj):
        return obj.group.slug if obj.group else None

    def get_group_name(self, obj):
        return obj.group.name if obj.group else None

    def get_contact(self, obj):
        return {'id': obj.user.gcrm_contact.id, 'name': obj.user.gcrm_contact.name}

    def get_balance(self, obj):
        from currencies.rest_fields import MoneyField
        try:
            return MoneyField().to_representation(obj.get_balance_money(with_bonus=True))
        except PlatformError as e:
            log.error(e)
            return None

    class Meta:
        model = TradingAccount
        fields = ('id', 'mt4_id', 'creation_ts', 'group_slug', 'group_name', 'contact', 'balance')


class ManagerStatsSerializer(serializers.Serializer):
    stats_date = serializers.DateTimeField()


class ManagerPasswordSerializer(serializers.Serializer):
    value = serializers.CharField(required=True, min_length=4, max_length=24)

    def save(self):
        self.instance.set_password(self.validated_data['value'])
        self.instance.save()
        Event.GCRM_MANAGER_SET_NEW_PASSWORD.log(self.instance)
        return self.instance


class ManagerNameSerializer(serializers.Serializer):
    last = serializers.CharField(required=True, min_length=1, max_length=32)
    first = serializers.CharField(required=True, min_length=1, max_length=32)
    middle = serializers.CharField(allow_blank=True, allow_null=True, max_length=32)

    def save(self):
        old_name = self.instance.profile.get_full_name()
        self.instance.first_name = self.validated_data['first']
        self.instance.last_name = self.validated_data['last']
        self.instance.save()
        self.instance.profile.middle_name = self.validated_data['middle']
        self.instance.profile.save()
        Event.GCRM_MANAGER_RENAME.log(self.instance, {
            'old_name': old_name,
            'new_name': self.instance.profile.get_full_name()
        })
        return self.instance


class ManagerEmailSerializer(serializers.Serializer):
    value = serializers.CharField(required=True, max_length=60)


class SetAsManagerSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=True)
    office = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=RegionalOffice.objects.none())

    def __init__(self, *a, **kwa):
        super(SetAsManagerSerializer, self).__init__(*a, **kwa)
        current_user = self.context['request'].user

        if current_user.is_superuser or current_user.crm_manager.is_head_supermanager:
            self.fields['office'].queryset = RegionalOffice.objects.all()
        elif current_user.crm_manager.is_office_supermanager:
            self.fields['office'].queryset = RegionalOffice.objects.filter(id=current_user.crm_manager.office_id)

    def validate_user(self, value):
        try:
            return User.objects.get(id=value)
        except User.DoesNotExists:
            raise serializers.ValidationError("User does not exists")

    def save(self):
        obj = PersonalManager.objects.create(allowed_ips='*', daily_limit=200, **self.validated_data)
        Event.GCRM_NEW_MANAGER_MANUALLY.log(obj.user, {'id': obj.id, 'office': obj.office_id})
        return obj


class ManagerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    office = serializers.SerializerMethodField()
    is_managable = serializers.SerializerMethodField()
    is_supermanager = serializers.SerializerMethodField()
    can_see_all_users = serializers.ReadOnlyField(source='crm_manager.can_see_all_users')

    def get_office(self, obj):
        if not obj.is_gcrm_manager:
            return None
        if not obj.crm_manager.office:
            return {'name': 'Главный', 'id': None}
        return {
            'name': obj.crm_manager.office.name,
            'id': obj.crm_manager.office.id
        }

    def get_is_managable(self, obj):
        if not obj.is_gcrm_manager:
            return False
        return user_can_manage(self.context['request'].user, obj)

    def get_is_supermanager(self, obj):
        return obj.is_superuser or (obj.is_gcrm_manager and obj.crm_manager.is_office_supermanager)

    def get_name(self, obj):
        return {
            'full': obj.profile.get_full_name(),
            'short': obj.profile.get_short_name(),
            'first': obj.profile.user.first_name,
            'last': obj.profile.user.last_name,
            'middle': obj.profile.middle_name
        }

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'office',
            'is_managable',
            'is_supermanager',
            'can_see_all_users',
        )


class ContactMinimalSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        if not obj.user:
            return None
        return {
            'id': obj.user.id,
            'registration_ts': obj.user.date_joined,
            'last_activity_ts': obj.user.profile.last_activity_ts,
            'last_activities': obj.user.profile.last_activity_translated,
            'name': obj.user.profile.get_full_name(),
            'location': {
                'address': ' '.join(filter(lambda x: x, [
                    getattr(obj.user.profile.country, 'name', None),
                    getattr(obj.user.profile.city, 'name', None),
                    getattr(obj.user.profile.state, 'name', None),
                ])),
                'timezone': getattr(obj.user.profile.get_time_zone(), 'zone', None)
            },
        }

    class Meta:
        model = Contact
        fields = (
            'id',
            'user',
            'name',
            'manager',
            'tags',
            'system_tags',
        )
        read_only_fields = (
            'id',
            'user',
            'name',
            'manager',
            'tags',
            'system_tags',
        )


class ContactSerializer(serializers.ModelSerializer):
    info = JSONSerializerField()
    user = serializers.SerializerMethodField()
    reassign_requests = ManagerReassignRequestSerializer(source="manager_reassign_requests.unresolved", many=True, read_only=True)

    def __init__(self, *args, **kwargs):
        super(ContactSerializer, self).__init__(*args, **kwargs)
        self.fields['manager'].queryset = User.objects \
            .filter(is_active=True) \
            .exclude(crm_manager=None)

    def validate_manager(self, value):
        current_user = self.context['request'].user
        if not self.instance and user_can_manage(current_user, value):
            return value
        if not (user_can_manage(current_user, self.instance.manager) and user_can_manage(current_user, value)):
            raise serializers.ValidationError("Необходимо создать заявку")
        return value

    def validate_tags(self, value):
        if not value:
            return value
        return [v.lower() for v in value]

    def get_user(self, obj):
        if not obj.user:
            return None

        current_user = self.context['request'].user

        def from_partner():
            from reports.models import AccountGroup
            return obj.user.profile.agent_code and obj.user.profile.agent_code in set(
                map(int, AccountGroup.objects.get(id=3).account_mt4_ids)
            )

        from push_notifications.models import GCMDevice, APNSDevice
        from django.core.urlresolvers import reverse
        return {
            'id': obj.user.id,
            'registration_ts': obj.user.date_joined,
            'last_activity_ts': obj.user.profile.last_activity_ts,
            'last_activities': obj.user.profile.last_activity_translated,
            'name': obj.user.profile.get_full_name(),
            'has_valid_documents': obj.user.profile.has_valid_documents(),
            'username': obj.user.username,
            'location': {
                'address': ' '.join(filter(lambda x: x, [
                    getattr(obj.user.profile.country, 'name', None),
                    getattr(obj.user.profile.city, 'name', None),
                    getattr(obj.user.profile.state, 'name', None),
                ])),
                'timezone': getattr(obj.user.profile.get_time_zone(), 'zone', None)
            },
            'language': obj.user.profile.params.get('registration_language', ''),
            'phone': {
                'value': obj.user.profile.phone_mobile,
                'is_verified': obj.user.profile.has_valid_phone()
            },
            'email': obj.user.email,

            'agent_code': {
                'value': obj.user.profile.agent_code,
                'from_partner': from_partner(),
                'contact': getattr(Contact.objects
                    .filter(user__accounts__mt4_id=obj.user.profile.agent_code)
                    .first(), 'id', None)
            },
            'otp': {
                'device': getattr(obj.user.profile.otp_device, 'type', None),
                'is_lost': obj.user.profile.lost_otp,
                'resetable': current_user.is_superuser or current_user.has_perm('gcrm.user_reset_otp')
            },
            'partnership': {
                'domains': [pd.domain for pd in obj.user.partner_domains.all()]
            },
            'documents': [{
                'name': doc.get_name_display(),
                'url': doc.file.url if current_user.crm_manager.has_document_access else ''
            } for doc in obj.user.documents.all()],
            'utm': {
                'utm_source': obj.user.utm_analytics.utm_source,
                'utm_medium': obj.user.utm_analytics.utm_medium,
                'utm_campaign': obj.user.utm_analytics.utm_campaign
            } if hasattr(obj.user, 'utm_analytics') else None,
            'links': {
                'user_admin': reverse('admin:auth_user_change', args=(obj.user.id,)),
                'user_profile_admin': reverse('admin:profiles_userprofile_change', args=(obj.user.profile.id,)),
            } if current_user.is_superuser else None,

        }

    # def get_similar(self, obj):
    #     return [{
    #         'name': similar.get_full_name(),
    #         'created_at': dt_format(similar.user.date_joined),
    #         'accounts_count': similar.user.accounts.active().count(),
    #         'manager': similar.manager.profile.get_full_name() if similar.manager else u'Нет',
    #         'amo_link': similar.get_amo().get_url()
    #     } for similar in obj.similar]

    def create(self, validated_data):
        # if manager is set on create, set assigned_ts
        if validated_data.get('manager'):
            validated_data['assigned_ts'] = datetime.now()
        obj = super(ContactSerializer, self).create(validated_data)
        Event.GCRM_CONTACT_CREATED.log(obj)
        return obj

    def update(self, instance, validated_data):
        # if manager is changed, set assigned_ts and remove is_assigned_by_button mark, log it
        if 'manager' in validated_data and validated_data['manager'] != instance.manager:
            instance.set_manager(validated_data['manager'])
        return super(ContactSerializer, self).update(instance, validated_data)

    class Meta:
        model = Contact
        fields = (
            'id',
            'user',
            'name',
            'manager',
            'reassign_requests',
            'info',
            'tags',
            'system_tags',
            'update_ts',
            'creation_ts',
        )
        read_only_fields = (
            'id',
            'user',
            'system_tags',
            'update_ts',
            'creation_ts',
        )


class ManagerReassignSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False)
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True).exclude(crm_manager=None),
        allow_null=True
    )

    class Meta:
        fields = ('manager', 'comment')

    def is_direct(self, to):
        current_user = self.context['request'].user
        return user_can_manage(current_user, self.instance.manager) and user_can_manage(current_user, to)

    def validate(self, data):
        if not self.is_direct(data['manager']) and not data.get('comment'):
            raise serializers.ValidationError({
                'comment': serializers.Field.default_error_messages['required']
            })
        return data

    def execute(self):
        req = ManagerReassignRequest(
            contact=self.instance,
            author=self.context['request'].user,
            comment=self.validated_data.get('comment') or '',
            new_manager=self.validated_data['manager'],
            previous_manager=self.instance.manager,
        )
        if self.is_direct(self.validated_data['manager']):
            req.accept(self.context['request'].user, _('Manager has been assigned manualy'))
            return {
                'status': 'changed',
                'detail': _('Manager has been assigned'),
                'object': ManagerReassignRequestSerializer(instance=req, context=self.context).data
            }

        if req.contact.manager_reassign_requests.unresolved().filter(new_manager=req.new_manager).exists():
            return {
                'status': 'request_exists',
                'detail': _('Reasign request to selected manager already exists')
            }

        req.save()
        return {
            'status': 'request_created',
            'detail': _('Reasign request has been created'),
            'object': ManagerReassignRequestSerializer(instance=req, context=self.context).data
        }


class BatchManagerReassignSerializer(serializers.Serializer):
    comment = serializers.CharField()
    new_manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True).exclude(crm_manager=None),
        allow_null=True
    )
    with_task = serializers.BooleanField()
    task_comment = serializers.CharField(allow_blank=True, required=False)
    set_agent_code = serializers.BooleanField()
    agent_code = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        fields = ('new_manager', 'comment')

    def validate(self, data):
        current_user = self.context['request'].user
        managers_ids = self.instance.distinct('manager').values_list('manager', flat=True)
        self.managers = list(User.objects.filter(id__in=managers_ids))
        if None in managers_ids:
            self.managers.append(None)
        if any(not user_can_manage(current_user, m) for m in self.managers+[data['new_manager']]) and self.instance.count() > 20:
            raise serializers.ValidationError({
                'new_manager': _('You can\'t select more than 20 contacts for indirect reassign')
            })
        if data.get('with_task', False) and 'task_comment' not in data:
            raise serializers.ValidationError({
                'task_comment': _('You must specify comment for a task')
            })
        if data.get('set_agent_code', False) and 'agent_code' not in data:
            raise serializers.ValidationError({
                'agent_code': _('You must specify agent code')
            })
        if data['set_agent_code']:
            self.bsacs = BatchContactAgentCodeSerializer(instance=self.instance, data={'code': data['agent_code']})
            try:
                self.bsacs.is_valid(raise_exception=True)
            except serializers.ValidationError as ve:
                raise serializers.ValidationError({
                    'agent_code': ve.detail['code']
                })
        return data

    def execute(self):
        current_user = self.context['request'].user
        new_manager = self.validated_data['new_manager']
        requests = []
        tasks = []
        for m in self.managers:
            is_direct = user_can_manage(current_user, m) and user_can_manage(current_user, new_manager)
            contacts = self.instance.filter(manager=m)
            for c in contacts:
                requests.append(ManagerReassignRequest(
                    contact=c,
                    author=current_user,
                    comment=self.validated_data.get('comment') or '',
                    new_manager=new_manager,
                    previous_manager=c.manager,
                    close_comment=_('Mass assignment') if is_direct else None,
                    closed_by=current_user if is_direct else None,
                    result=True if is_direct else None,
                    with_task=self.validated_data.get('task_comment', '') if self.validated_data['with_task'] else ''
                ))
            if is_direct:
                contacts.set_manager(new_manager, comment=self.validated_data.get('comment'))
                unresolved = ManagerReassignRequest.objects.unresolved().filter(
                    new_manager=new_manager,
                    contact__in=contacts)
                for req in unresolved:
                    req.accept(current_user, _('Mass assignment'), child=True)

                if self.validated_data['with_task']:
                    task_comment = self.validated_data.get('task_comment', '')
                    for c in contacts:
                        tasks.append(Task(contact=c,
                                          author=current_user,
                                          text=task_comment,
                                          assignee=new_manager,
                                          deadline=datetime.now().replace(hour=23, minute=59, second=59)))

        ManagerReassignRequest.objects.bulk_create(requests)
        Task.objects.bulk_create(tasks)
        if self.validated_data['set_agent_code']:
            self.bsacs.execute()

        return {
            'status': 'success',
            'detail': _('Reassign requests was created'),
        }


class BatchContactAgentCodeSerializer(serializers.Serializer):
    code = serializers.CharField(allow_blank=True)

    class Meta:
        fields = ('code')

    def validate(self, data):
        code = data['code']
        if not code.isdigit():
            raise serializers.ValidationError({
                'code': _('Code must be a number')
            })
        ag = AccountGroup.objects.get(id=3)
        ids = set(map(int, ag.account_mt4_ids))
        if not (code == '0' or code in ids or TradingAccount.objects.real_ib().filter(mt4_id=code)):
            raise serializers.ValidationError({
                'code': _('This code does not exists')
            })
        return data

    def execute(self):
        code = self.validated_data['code']
        for contact in self.instance:
            contact.user.profile.agent_code = int(code) if code != '0' else None
            contact.user.profile.save()
        TradingAccount.objects.filter(user__gcrm_contact__in=self.instance).bulk_change_agent_account(int(code))

        return {
            'status': 'success',
            'detail': _('Agent code was updated successfully'),
        }
        #  если 0 то снять код агента


class NoteSerializer(serializers.ModelSerializer):
    feed_type = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    is_editable = serializers.SerializerMethodField()

    def get_contact(self, obj):
        data = {
            'id': obj.contact_id,
            'name': obj.contact.name,
            'manager': obj.contact.manager_id,
            'tags': obj.contact.system_tags + obj.contact.tags,
        }
        return data

    def get_is_editable(self, obj):
        current_user = self.context['request'].user
        return obj.is_editable_by(current_user)

    def get_feed_type(self, obj):
        return 'note'

    class Meta:
        model = Note
        fields = (
            'id',
            'contact',
            'author',
            'text',
            'is_editable',
            'update_ts',
            'creation_ts',
            'feed_type',
        )
        read_only_fields = (
            'id',
            'contact',
            'author',
            'update_ts',
            'creation_ts',
        )


class TaskSerializer(serializers.ModelSerializer):
    feed_type = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    is_completable = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()
    is_editable = serializers.SerializerMethodField()
    deadline = serializers.DateTimeField(default_timezone=timezone.UTC())

    def validate_deadline(self, value):
        return timezone.make_naive(value)

    def get_contact(self, obj):
        data = {
            'id': obj.contact_id
        }
        if 'view' in self.context:
            data.update({
                'name': obj.contact.name,
                'manager': obj.contact.manager_id,
                'tags': obj.contact.system_tags + obj.contact.tags,
            })
        return data

    def get_is_completable(self, obj):
        current_user = self.context['request'].user
        return obj.is_completable_by(current_user)

    def get_is_editable(self, obj):
        current_user = self.context['request'].user
        return obj.is_editable_by(current_user)

    def get_feed_type(self, obj):
        return 'task'

    class Meta:
        model = Task
        fields = (
            'id',
            'contact',
            'author',
            'task_type',
            'text',
            'assignee',
            'deadline',
            'is_completable',
            'is_editable',
            'is_expired',

            'closed_at',
            'close_comment',

            'update_ts',
            'creation_ts',
            'feed_type',
        )
        read_only_fields = (
            'id',
            'contact',
            'author',
            'is_completable',
            'is_editable',
            'closed_at',
            'close_comment',
            'update_ts',
            'creation_ts',
            'feed_type',
        )


class TaskCompleteSerializer(serializers.Serializer):
    note = serializers.CharField()

    class Meta:
        fields = ('note',)

    def validate(self, data):
        if self.instance.is_completed:
            raise serializers.ValidationError("Задача уже завершена")
        return data

    def save(self):
        self.instance.closed_at = datetime.now()
        self.instance.close_comment = self.validated_data['note']

        # just override assignee when someone completes task
        self.instance.assignee = self.context['request'].user
        self.instance.save()
        return {
            'detail': 'okay',
            'object': TaskSerializer(instance=self.instance, context=self.context).data,
        }


class FeedAccountSerializer(serializers.ModelSerializer):
    feed_type = serializers.SerializerMethodField()
    group = serializers.ReadOnlyField(source="group.slug")
    group_name = serializers.ReadOnlyField(source="group.name")
    balance = MoneyField(source="balance_money")
    equity = MoneyField(source="equity_money")
    leverage = serializers.ReadOnlyField()
    is_demo = serializers.ReadOnlyField()
    bonus_details = serializers.SerializerMethodField()

    def get_bonus_details(self, obj):
        return {}

    def get_feed_type(self, obj):
        return 'mt4account'

    def get_bonuses(self, obj):
        from currencies.money import Money
        return [{
            'name': slug,
            'money': unicode(Money(*money_tuple)),
        } for slug, money_tuple in obj.get_bonus_details().items()]

    class Meta:
        model = TradingAccount
        fields = (
            'id',
            'mt4_id',
            'is_deleted',

            'balance',
            'equity',
            'leverage',

            'group_name',
            'is_demo',
            'group',

            'creation_ts',
            'feed_type',
            'bonus_details',
        )


class FeedDepositRequestSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    feed_type = serializers.SerializerMethodField()
    payment_system = serializers.ReadOnlyField(source='payment_system.__unicode__')
    amount = MoneyField(source='amount_money')
    amount_USD = serializers.SerializerMethodField()
    status = serializers.ReadOnlyField()
    account = serializers.SerializerMethodField()

    def get_feed_type(self, obj):
        return 'payment'

    def get_type(self, obj):
        return 'deposit' if obj.is_deposit else 'withdraw'

    def get_account(self, obj):
        return {
            'mt4_id': obj.account.mt4_id,
            'group': obj.account.group.slug if obj.account.group else "None",
            'group_name': obj.account.group.name if obj.account.group else "None",
        }

    def get_amount_USD(self, obj):
        return MoneyField().to_representation(obj.amount_money.to_USD())

    class Meta:
        model = DepositRequest
        fields = (
            'id',
            'type',
            'amount',
            'amount_USD',
            'status',
            'payment_system',
            'account',

            'payment_system',
            'private_comment',
            'public_comment',

            'creation_ts',
            'feed_type',
        )


class FeedWithdrawRequestSerializer(FeedDepositRequestSerializer):
    class Meta:
        model = WithdrawRequest
        fields = FeedDepositRequestSerializer.Meta.fields + ('group',)


class FeedCallSerializer(serializers.ModelSerializer):
    feed_type = serializers.SerializerMethodField()
    record = serializers.SerializerMethodField()
    a = serializers.ReadOnlyField(source='source_str')
    b = serializers.ReadOnlyField(source='dest_str')

    def get_record(self, obj):
        return obj.get_record_path()

    def get_feed_type(self, obj):
        return 'call'

    class Meta:
        model = CallDetailRecord
        fields = (
            'id',
            'call_date',
            'a',
            'b',
            'duration',
            'disposition',
            'record',
            'feed_type',
        )


class FeedLogSerializer(serializers.ModelSerializer):
    feed_type = serializers.SerializerMethodField()
    user = ManagerSerializer()
    params = serializers.SerializerMethodField()
    object_string = serializers.ReadOnlyField(source='content_object.__unicode__')

    def get_params(self, obj):
        params = {}
        for k, v in obj.params.iteritems():
            if isinstance(v, User):
                params[k] = ManagerSerializer(v, context=self.context).data
            else:
                params[k] = v
        return params

    def get_feed_type(self, obj):
        return 'log'

    class Meta:
        model = Logger
        fields = (
            'id',
            'feed_type',
            'object_string',
            'user',
            'ip',
            'at',
            'params',
            'event',
        )


class CallSerializer(serializers.ModelSerializer):
    record = serializers.SerializerMethodField()
    a = serializers.SerializerMethodField()
    b = serializers.SerializerMethodField()
    call_date = serializers.DateTimeField()

    def get_record(self, obj):
        return obj.get_record_path()

    def get_a(self, obj):
        if obj.user_a:
            return {"id": obj.user_a.gcrm_contact.id,
                    "name": obj.user_a.gcrm_contact.name}
        else:
            return u"{0}({1})".format(
                obj.safe_number_a,
                'External' if obj.name_a and '@' in obj.name_a else obj.name_a)

    def get_b(self, obj):
        if obj.user_b:
            return {"id": obj.user_b.gcrm_contact.id,
                    "name": obj.user_b.gcrm_contact.name}
        else:
            return u"{0}({1})".format(
                obj.safe_number_b,
                'External' if obj.name_b and '@' in obj.name_b else obj.name_b)

    class Meta:
        model = CallDetailRecord
        fields = (
            'id',
            'call_date',
            'a',
            'b',
            'duration',
            'disposition',
            'record',
        )


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'id',
            'name',
        )


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = (
            'id',
            'name',
        )


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'language',
        )
