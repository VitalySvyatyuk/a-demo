# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db.models import Q, F, Func, Count
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet, MethodFilter
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from crm.assignment_logic import possible_clients_for
from crm.models import PersonalManager
from currencies.money import Money
from gcrm.models import Contact, ManagerReassignRequest, Task, Note
from gcrm.rest.filter_fields import TagFilter, TypesFilter, ManagerFilterField, AssigneeFilter,\
    DateTimeFromToRangeFilter, ResultsFilter, AccountTypeFilter, StatusFilter, ManagerFilterMultipleField, \
    DispositionFilter, CountriesFilter, RegionsFilter, MultipleMethodFilter, LanguagesFilter
from gcrm.rest.permissions import HasCRMAccess, HasContactsLimit
from gcrm.utils import user_can_manage, can_user_set_agent_codes
from geobase.models import Country, Region
from log.models import Event, Logger
from platforms.types import get_account_type
from payments.models import DepositRequest, WithdrawRequest
from platforms.models import TradingAccount
from telephony.models import CallDetailRecord
from .serializers import (
    ContactSerializer, ContactMinimalSerializer, ManagerSerializer,
    ManagerReassignSerializer, ManagerReassignRequestSerializer,
    RejectReassignRequestSerializer, ManagerStatsSerializer, CallSerializer,
    ManagerPasswordSerializer, ManagerNameSerializer, ManagerEmailSerializer,
    SetAsManagerSerializer, BatchManagerReassignSerializer, BatchContactAgentCodeSerializer,
    CountrySerializer, RegionSerializer,  # Feed parts
    TaskSerializer, NoteSerializer, FeedAccountSerializer,
    TaskCompleteSerializer, FeedCallSerializer,
    FeedDepositRequestSerializer, FeedWithdrawRequestSerializer,
    AccountSerializer, FeedLogSerializer,)

import re

class ManagerStatsFilter(FilterSet):
    stats_date = DateTimeFromToRangeFilter()

    class Meta:
        model = User
        fields = ['stats_date']


class ManagerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [HasCRMAccess]
    queryset = User.objects \
        .exclude(crm_manager=None) \
        .filter(Q(is_active=True) | ~Q(gcrm_contacts=None)) \
        .select_related('profile', 'crm_manager', 'crm_manager__office') \
        .order_by('crm_manager__office')

    # local office sees everything
    # parter - only self
    serializer_class = ManagerSerializer
    paginator = None

    @list_route()
    def get_info(self, request):
        user_tasks = Task.objects.filter(assignee=request.user)
        context = self.get_serializer_context()
        serialize_tasks = lambda tasks: TaskSerializer(tasks, many=True, context=context).data

        count = -1
        if request.user.crm_manager.can_request_new_customers:
            clients, count = possible_clients_for(request.user)
        return Response({
            'tasks': {
                'overdue': serialize_tasks(user_tasks.filter(closed_at=None, deadline__lte=datetime.now())[:4]),
                'next': serialize_tasks(user_tasks.filter(closed_at=None, deadline__gt=datetime.now()).order_by('deadline')[:4])
            },
            'clients': {
                'free': count
            },
            'counts': {
                'overdue': user_tasks.filter(closed_at=None, deadline__lte=datetime.now()).count(),
                'next': user_tasks.filter(
                            closed_at=None,
                            deadline__range=(datetime.now(), datetime.now()+timedelta(days=1)))
                        .order_by('deadline').count(),
                'reassign': ManagerReassignRequestViewSet.get_base_queryset(user=request.user).filter(result__isnull=True).count()
            }
        })

    @list_route(serializer_class=ManagerStatsSerializer)
    def get_stats(self, request):
        filters = ManagerStatsFilter(request.query_params)
        assert filters.form.is_valid()
        stats_date = filters.form.cleaned_data['stats_date']
        managers = [m for m in self.get_queryset() if user_can_manage(self.request.user, m)]
        data = PersonalManager.manager_stats(
            managers,
            stats_date.start if stats_date else None,
            stats_date.stop if stats_date else None)
        for d in data:
            d['manager'] = d['manager'] and d['manager'].pk
        return Response(data=data)

    @detail_route(methods=['post'], serializer_class=ManagerPasswordSerializer)
    def set_password(self, request, pk=None):
        user = self.get_object()
        if not user_can_manage(self.request.user, user):
            raise PermissionDenied()
        serializer = self.get_serializer(data=request.data, instance=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': "Successfully changed password"})

    @detail_route(methods=['post'])
    def revoke(self, request, pk=None):
        user = self.get_object()
        if not user_can_manage(self.request.user, user):
            raise PermissionDenied()

        if Contact.objects.filter(manager=user).count():
            return Response({
                'detail': "Can't delete users with contacts! Please reassigned contacts and try again."
            }, status=409)

        user.crm_manager.delete()
        Event.GCRM_MANAGER_REVOKE.log(user)
        return Response({'detail': "Successfully revoked user"})

    @detail_route(methods=['post'], serializer_class=ManagerNameSerializer)
    def set_name(self, request, pk=None):
        user = self.get_object()
        if not user_can_manage(self.request.user, user):
            raise PermissionDenied()
        serializer = self.get_serializer(data=request.data, instance=user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'object': ManagerSerializer(user, context=serializer.context).data
        })

    @list_route(methods=['post'], serializer_class=SetAsManagerSerializer)
    def set_as_manager(self, request):
        if not (request.user.is_superuser or request.user.crm_manager.is_office_supermanager):
            raise PermissionDenied()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response({
            'object': ManagerSerializer(obj.user, context=serializer.context).data
        })

    @list_route(methods=['get'], serializer_class=ManagerEmailSerializer)
    def find_managers(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        value = serializer.validated_data['value']
        data = [{'id': item.pk,
                 'name': item.profile.get_full_name()}
                for item in User.objects.filter(crm_manager=None).
                                filter(Q(email__icontains=value) | Q(profile__phone_mobile__icontains=value))[:5]]
        return Response(data=data)

    @detail_route(methods=['get'])
    def can_set_agent_codes(self, request, pk):
        user = get_object_or_404(self.get_queryset(), pk=pk)
        return Response({'can_set_agent_codes': can_user_set_agent_codes(user)})


class ContactFilter(FilterSet):
    search = MethodFilter()
    tags = TagFilter()
    manager = ManagerFilterField('manager')
    user__date_joined = DateTimeFromToRangeFilter()
    user__profile__last_activity_ts = DateTimeFromToRangeFilter()
    countries = CountriesFilter()
    regions = RegionsFilter()
    languages = LanguagesFilter()

    class Meta:
        model = Contact
        fields = ['manager', 'search', 'tags', 'user__date_joined', 'user__profile__last_activity_ts',
                  'countries', 'regions', 'languages']

    def filter_search(self, queryset, value):
        if not value:
            return queryset

        searches = Q()
        for word in value.strip().split():
            agent_code = re.match(r'ib:(\d+)', word)
            if agent_code:
                searches &= Q(user__profile__agent_code=agent_code.groups()[0])
            else:
                searches &= (
                    Q(name__icontains=word) |
                    Q(info__icontains=word) |
                    Q(search_cache__icontains=word) |

                    Q(user__username__icontains=word) |
                    Q(user__email__icontains=word) |
                    Q(user__last_name__icontains=word) |
                    Q(user__first_name__icontains=word) |
                    Q(user__profile__middle_name__icontains=word) |
                    Q(user__profile__phone_mobile__icontains=word) |

                    Q(user__accounts__mt4_id__icontains=word)
                )
        return queryset.filter(searches)


class ContactViewSet(viewsets.ModelViewSet):
    permission_classes = [HasCRMAccess, HasContactsLimit]
    filter_class = ContactFilter
    ordering_fields = ['name', 'manager', 'user__date_joined', 'user__profile__last_activity_ts']
    ordering = 'name'

    @classmethod
    def get_base_queryset(cls, user, params=None, qs=None):
        if qs is None:
            qs = Contact.objects.all()

        # hack to force join on user, which we'll need to calc composited fields
        if user.is_superuser or user.crm_manager.is_head_supermanager or user.crm_manager.can_see_all_users:
            pass
        elif user.crm_manager.is_office_supermanager:
            qs = qs.filter(manager__crm_manager__office=user.crm_manager.office)
        else:
            qs = qs.filter(manager=user)

        if params and params.getlist('id'):
            qs = qs.filter(pk__in=params.getlist('id'))
        return qs

    def get_queryset(self):
        qs = self.get_base_queryset(self.request.user, params=self.request.query_params)
        filter = self.filter_class(
            data=self.request.query_params,
            queryset=qs
        )
        if not filter.form.is_valid():
            raise Exception(filter.form.errors)
        qs = filter.qs
        qs = qs.prefetch_related('user', 'user__profile', 'user__profile__country', 'user__profile__state', 'user__profile__state__country')
        return qs

    def get_queryset_summary(self):
        all_tags = Func(F('tags'), F('system_tags'), function='array_cat')
        return {
            'tags': self.get_queryset().annotate(
                tag=Func(all_tags, function='unnest')
            ).values('tag').annotate(count=Count('tag')),
            'managers': self.get_queryset().values('manager').annotate(count=Count('manager'))
        }

    def get_serializer_class(self, *a, **kwa):
        # avoid overriden in actions serializer override
        if self.serializer_class:
            return self.serializer_class

        if self.action == 'list':
            return ContactMinimalSerializer
        return ContactSerializer

    @detail_route()
    def feed(self, request, pk=None):
        """
        This mega-function forms json data for gcrm feed view.
        It serializes many things in one chunk.
        """
        from contextlib import contextmanager
        import time

        # TODO: what's this?
        @contextmanager
        def tit(name):
            startTime = time.time()
            yield
            elapsedTime = time.time() - startTime
            print('[{}] finished in {} ms'.format(name, int(elapsedTime * 1000)))


        obj = self.get_object()
        context = self.get_serializer_context()
        feed_type = request.query_params.get('type')
        offset = int(request.query_params.get('offset', 0))
        limit = int(request.query_params.get('limit', 100))

        feed = []
        now = datetime.now()

        # Big big IF to determine what data to be serialized
        if not feed_type or feed_type == 'record':
            qs = Task.objects.prefetch_related('contact', 'assignee', 'author')
            for id, closed_at, deadline in obj.tasks.all().order_by('-closed_at', '-deadline').values_list('id', 'closed_at', 'deadline'):
                feed.append((
                    closed_at or (deadline if deadline > now else (deadline + timedelta(365))),
                    {'qs': qs, 'id': id}
                ))

            qs = Note.objects.prefetch_related('contact', 'author')
            for id, ts in obj.notes.all().order_by('-update_ts').values_list('id', 'update_ts'):
                feed.append((ts, {'qs': qs, 'id': id}))

        if obj.user:
            if not feed_type or feed_type == 'mt4account':
                qs = TradingAccount.objects.all()
                for id, ts in obj.user.accounts.order_by('-creation_ts').values_list('id', 'creation_ts'):
                    feed.append((ts, {'qs': qs, 'id': id}))

            if not feed_type or feed_type == 'payment':
                qs = DepositRequest.objects.prefetch_related('account', 'account__user')
                for id, ts in DepositRequest.objects.filter(account__user=obj.user).values_list('id', 'creation_ts'):
                    feed.append((ts, {'qs': qs, 'id': id}))

                qs = WithdrawRequest.objects.prefetch_related('account', 'account__user')
                for id, ts in WithdrawRequest.objects.filter(account__user=obj.user).values_list('id', 'creation_ts'):
                    feed.append((ts, {'qs': qs, 'id': id}))

        if not feed_type or feed_type == 'call':
            qs = CallDetailRecord.objects.prefetch_related('user_a', 'user_b')
            for id, ts in obj.calls.all().values_list('id', 'call_date'):
                feed.append((ts, {'qs': qs, 'id': id}))

        if not feed_type or feed_type == 'log':
            qs = Logger.objects.all().prefetch_params()
            for id, ts in obj.logs.values_list('id', 'at'):
                feed.append((ts, {'qs': qs, 'id': id}))
        if feed_type == 'fulllog':
            qs = Logger.objects.all().prefetch_params()
            for id, ts in obj.related_logs.values_list('id', 'at'):
                feed.append((ts, {'qs': qs, 'id': id}))

        feed.sort(reverse=True)

        total = len(feed)
        # Cut output
        feed = feed[offset:offset + limit]

        # Form resonse?
        instances = {}
        for d, rec in feed:
            instances.setdefault(rec['qs'], []).append(rec['id'])
        instances = {
            qs.model: {o.pk: o for o in qs.filter(pk__in=ids)}
            for qs, ids in instances.items()
        }

        # Serializers to use for different data types
        serializers = {
            Task: TaskSerializer,
            Note: NoteSerializer,
            TradingAccount: FeedAccountSerializer,
            DepositRequest: FeedDepositRequestSerializer,
            WithdrawRequest: FeedWithdrawRequestSerializer,
            CallDetailRecord: FeedCallSerializer,
            Logger: FeedLogSerializer
        }

        # TODO: what's this ololo?
        with Money.convert_cache_key('ololo'):
            feed = [
                serializers[rec['qs'].model](
                    instance=instances[rec['qs'].model][rec['id']],
                    context=context
                ).data for d, rec in feed]

        # Final response
        return Response({
            'items': feed,
            'total': total
        }, status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['post'], serializer_class=ManagerReassignSerializer)
    def reassign(self, request, pk=None):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.execute(), status=status.HTTP_202_ACCEPTED)

    @list_route(methods=['post'], serializer_class=BatchManagerReassignSerializer)
    def batch_reassign(self, request):
        current_user = request.user
        if request.data.get('set_agent_code', False) and not can_user_set_agent_codes(current_user):
            raise PermissionDenied("You are not allowed to update agent code")
        serializer = self.get_serializer(instance=self.get_queryset(), data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.execute(), status=status.HTTP_202_ACCEPTED)

    @list_route(methods=['post'], serializer_class=BatchContactAgentCodeSerializer)
    def batch_agent_code(self, request):
        current_user = request.user
        if not can_user_set_agent_codes(current_user):
            raise PermissionDenied("You are not allowed to update agent code")
        serializer = self.get_serializer(instance=self.get_queryset(), data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.execute(), status=status.HTTP_202_ACCEPTED)

    @list_route()
    def get_next_client(self, request):
        if not request.user.crm_manager.can_request_new_customers:
            raise PermissionDenied("No, no, you can't get new customers :|")

        last = Contact.objects.filter(manager=request.user, is_assigned_by_button=True).order_by('-assigned_ts').first()
        if False and last and request.user.crm_manager.needs_call_check:
            last_call = last.calls.from_user(request.user, with_phone=False).order_by('-call_date').first()
            if not last_call or last_call.call_date < last.assigned_ts:
                return Response({
                    'detail': _("To get a new client, you need to make a call to the previous one"),
                    'last_id': last.gcrm_contact.pk
                }, status=status.HTTP_403_FORBIDDEN)

        if last and (datetime.now() - last.assigned_ts) < timedelta(seconds=10):
            return Response({'detail': "Too fast! slowpoke.jpg"}, status=status.HTTP_403_FORBIDDEN)

        new_contact = getattr(possible_clients_for(request.user)[0].first(), 'gcrm_contact', None)
        if not new_contact:
            return Response({'detail': _("There are no available clients")}, status=status.HTTP_404_NOT_FOUND)

        new_contact.set_manager(request.user, event=Event.GCRM_MANAGER_CHANGED_BY_BUTTON)
        new_contact.manager = request.user
        new_contact.assigned_ts = datetime.now()
        new_contact.is_assigned_by_button = True
        new_contact.save()

        new_contact.add_task(text=_("First contact with the client"))

        return Response({'id': new_contact.pk})

    @detail_route(methods=['post'])
    def user_reset_otp(self, request, pk=None):
        if not request.user.has_perm('gcrm.user_reset_otp'):
            return Response(status=status.HTTP_404_NOT_FOUND)
        obj = self.get_object()
        if not obj.user.profile.lost_otp:
            obj.user.profile.delete_otp_devices(lost_otp=True)
            Event.OTP_IS_LOST.log(obj)
        return Response(status=status.HTTP_202_ACCEPTED)


class ReassignFilter(FilterSet):
    search = MethodFilter()
    result = ResultsFilter()
    author = ManagerFilterField('author')
    new_manager = ManagerFilterField('new_manager')
    previous_manager = ManagerFilterField('previous_manager')
    creation_ts = DateTimeFromToRangeFilter()

    class Meta:
        model = ManagerReassignRequest
        fields = ['search', 'result', 'new_manager', 'previous_manager', 'creation_ts', 'author']

    def filter_search(self, queryset, value):
        if not value:
            return queryset

        searches = Q()
        for word in value.strip().split():
            searches &= (
                Q(comment__icontains=word) |
                Q(close_comment__icontains=word)
            )
        return queryset.filter(searches)


class ManagerReassignRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [HasCRMAccess]
    serializer_class = ManagerReassignRequestSerializer
    ordering_fields = '__all__'
    ordering = ['-creation_ts']

    filter_class = ReassignFilter

    @classmethod
    def get_base_queryset(cls, user, params=None, qs=None):
        if user.is_superuser or user.crm_manager.is_head_supermanager:
            qs = ManagerReassignRequest.objects.all()
        elif user.crm_manager.is_office_supermanager:
            qs = ManagerReassignRequest.objects.filter(
                author__crm_manager__office=user.crm_manager.office,
                new_manager__crm_manager__office=user.crm_manager.office,
                previous_manager__crm_manager__office=user.crm_manager.office)
        else:
            qs = ManagerReassignRequest.objects.filter(author=user)
        qs |= ManagerReassignRequest.objects.filter(new_manager=user)
        qs |= ManagerReassignRequest.objects.filter(previous_manager=user)
        qs |= ManagerReassignRequest.objects.filter(author=user)
        return qs

    def get_queryset(self):
        qs = self.get_base_queryset(self.request.user, params=self.request.query_params)
        filter_type = self.request.query_params.get('type')
        if filter_type == 'unresolved':
            qs = qs.unresolved()
        # filters
        filter = self.filter_class(
            data=self.request.query_params,
            queryset=qs
        )
        if not filter.form.is_valid():
            raise Exception(filter.form.errors)
        qs = filter.qs
        return qs

    @detail_route(methods=['post'])
    def accept(self, request, pk=None):
        instance = self.get_object()
        if not instance.is_editable_by(request.user):
            raise PermissionDenied()
        instance.accept(closed_by=request.user)
        return Response({}, status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['post'], serializer_class=RejectReassignRequestSerializer)
    def reject(self, request, pk=None):
        instance = self.get_object()
        if not instance.is_editable_by(request.user):
            raise PermissionDenied()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(closed_by=request.user, result=False)
        return Response({}, status=status.HTTP_202_ACCEPTED)


class TaskFilter(FilterSet):
    deadline = DateTimeFromToRangeFilter()
    is_completed = MethodFilter()
    search = MethodFilter()
    assignee = AssigneeFilter()
    task_type = TypesFilter()
    status = StatusFilter()

    class Meta:
        model = Task
        fields = ['deadline', 'is_completed', 'search', 'assignee', 'task_type', 'status']

    def filter_is_completed(self, queryset, value):
        bool_value = {'false': False, 'true': True}.get(value, None)
        if bool_value is not None:
            return queryset.filter(closed_at__isnull=not bool_value)
        return queryset

    def filter_search(self, queryset, value):
        if not value:
            return queryset

        searches = Q()
        for word in value.strip().split():
            searches &= (
                Q(text__icontains=word) |
                Q(contact__name__icontains=word)
            )

        return queryset.filter(searches)


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [HasCRMAccess]
    serializer_class = TaskSerializer
    filter_class = TaskFilter
    ordering = 'deadline'
    ordering_fields = ['deadline', 'contact']

    @classmethod
    def get_base_queryset(cls, user, params=None, qs=None):
        if not qs:
            qs = Task.objects.all()
        if user.is_superuser or user.crm_manager.is_head_supermanager:
            pass
        elif user.crm_manager.is_office_supermanager:
            qs = qs.filter(
                # assigned to my ppl
                Q(assignee__crm_manager__office=user.crm_manager.office) |
                # assigned by my ppl
                Q(author__crm_manager__office=user.crm_manager.office)
            )
        else:
            qs = qs.filter(
                # assigned to me
                Q(assignee=user) |
                # assigned by me
                Q(author=user)
            )
        return qs

    def get_queryset(self):
        qs = self.get_base_queryset(self.request.user, params=self.request.query_params)
        filter = self.filter_class(
            data=self.request.query_params,
            queryset=qs
        )
        if not filter.form.is_valid():
            raise Exception(filter.form.errors)
        qs = filter.qs
        if self.action == 'list':
            qs = qs.prefetch_related('contact__user', 'contact__user__profile')
        return qs.prefetch_related('assignee', 'author', 'contact')

    def perform_create(self, serializer):
        contact = ContactViewSet.get_base_queryset(self.request.user).get(id=self.request.query_params.get('contact'))
        task = serializer.save(
            author=self.request.user,
            contact=contact
        )
        if task.assignee != task.author:
            task.send_creation_notification()

    def perform_update(self, serializer):
        if not serializer.instance.is_editable_by(self.request.user):
            raise PermissionDenied()
        serializer.save()

    def perform_destroy(self, instance):
        if not instance.is_editable_by(self.request.user):
            raise PermissionDenied()
        instance.delete()

    @detail_route(methods=['post'], serializer_class=TaskCompleteSerializer)
    def complete(self, request, pk=None):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save(), status=status.HTTP_202_ACCEPTED)
    #
    # @detail_route(methods=['post'], serializer_class=TaskPostponeSerializer)
    # def postpone(self, request, pk=None):
    #     serializer = self.get_serializer(instance=self.get_object(), data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     return Response(serializer.save(), status=status.HTTP_202_ACCEPTED)


class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = [HasCRMAccess]
    serializer_class = NoteSerializer

    def get_queryset(self):
        qs = Note.objects.all()
        if self.request.user.is_superuser or self.request.user.crm_manager.is_head_supermanager:
            pass
        elif self.request.user.crm_manager.is_office_supermanager:
            qs = qs.filter(author__crm_manager__office=self.request.user.crm_manager.office)
        else:
            qs = qs.filter(author=self.request.user)
        return qs

    def perform_create(self, serializer):
        contact = ContactViewSet.get_base_queryset(self.request.user).get(id=self.request.query_params.get('contact'))
        serializer.save(
            author=self.request.user,
            contact=contact)

    def perform_update(self, serializer):
        if not serializer.instance.is_editable_by(self.request.user):
            raise PermissionDenied()
        serializer.save()

    def perform_destroy(self, instance):
        if not instance.is_editable_by(self.request.user):
            raise PermissionDenied()
        instance.delete()


class AccountFilter(FilterSet):
    creation_ts = DateTimeFromToRangeFilter()
    search = MethodFilter()
    type = AccountTypeFilter()

    class Meta:
        model = TradingAccount
        fields = ['creation_ts', 'search', 'type']

    def filter_search(self, queryset, value):
        if not value:
            return queryset

        searches = Q()
        for word in value.strip().split():
            searches &= (
                Q(mt4_id__icontains=word) |
                Q(user__gcrm_contact__name__icontains=word)
            )
        return queryset.filter(searches)


class AccountViewSet(viewsets.ModelViewSet):
    permission_classes = [HasCRMAccess]
    serializer_class = AccountSerializer
    filter_class = AccountFilter
    ordering = '-creation_ts'
    ordering_fields = ['mt4_id', 'creation_ts', 'user__gcrm_contact__name', 'type']

    @classmethod
    def get_base_queryset(cls, user, params=None, qs=None):
        if not qs:
            qs = TradingAccount.objects.all()
        if user.is_superuser or user.crm_manager.is_head_supermanager or user.crm_manager.can_see_all_users:
            pass
        elif user.crm_manager.is_office_supermanager:
            qs = qs.filter(user__gcrm_contact__manager__crm_manager__office=user.crm_manager.office)
        else:
            qs = qs.filter(user__gcrm_contact__manager=user)
        return qs

    def get_queryset(self):
        qs = self.get_base_queryset(self.request.user, params=self.request.query_params)
        # filters
        filter = self.filter_class(
            data=self.request.query_params,
            queryset=qs
        )
        if not filter.form.is_valid():
            raise Exception(filter.form.errors)
        qs = filter.qs
        return qs.prefetch_related('user__gcrm_contact')

    @list_route()
    def get_types(self, request):
        all_types = list(set(map(get_account_type, TradingAccount.objects.all().order_by().distinct('group_name').values_list('group_name', flat=True))))
        return Response({type.slug: type.name for type in all_types if not type is None})


class CallFilter(FilterSet):
    call_date = DateTimeFromToRangeFilter()
    manager = ManagerFilterMultipleField(['user_a', 'user_b'])
    disposition = DispositionFilter()
    search = MethodFilter()

    class Meta:
        model = CallDetailRecord
        fields = ['call_date', 'manager', 'disposition', 'search']

    def filter_search(self, queryset, value):
        if not value:
            return queryset
        return queryset.filter(Q(number_a__contains=value) | Q(number_b__contains=value))


class CallViewSet(viewsets.ModelViewSet):
    permission_classes = [HasCRMAccess]
    serializer_class = CallSerializer
    filter_class = CallFilter
    ordering = '-call_date'
    ordering_fields = ['call_date']

    @classmethod
    def get_base_queryset(cls, user, params=None, qs=None):
        if not qs:
            qs = CallDetailRecord.objects.all()
        if user.is_superuser or user.crm_manager.is_head_supermanager or user.crm_manager.can_see_all_users:
            pass
        elif user.crm_manager.is_office_supermanager:
            qs = qs.filter(Q(user_a__crm_manager__office=user.crm_manager.office) |
                           Q(user_b__crm_manager__office=user.crm_manager.office))
        else:
            qs = qs.filter(Q(user_a=user) | Q(user_b=user))
        return qs

    def get_queryset(self):
        qs = self.get_base_queryset(self.request.user, params=self.request.query_params)
        # filters
        filter = self.filter_class(
            data=self.request.query_params,
            queryset=qs
        )
        if not filter.form.is_valid():
            raise Exception(filter.form.errors)
        qs = filter.qs
        return qs


class CountryFilter(FilterSet):
    search = MethodFilter()
    ids = MultipleMethodFilter()

    class Meta:
        model = Country
        fields = ['name']

    def filter_search(self, queryset, value):
        if not value:
            return queryset
        return queryset.filter(name__icontains=value)

    def filter_ids(self, queryset, value):
        if not value:
            return queryset
        return queryset.filter(pk__in=value)


class CountryViewSet(viewsets.ModelViewSet):
    permission_classes = [HasCRMAccess]
    serializer_class = CountrySerializer
    filter_class = CountryFilter
    ordering = ('weight', 'name',)

    @classmethod
    def get_base_queryset(cls, params=None, qs=None):
        return Country.objects.all()

    def get_queryset(self):
        qs = self.get_base_queryset(params=self.request.query_params)
        # filters
        filter = self.filter_class(
            data=self.request.query_params,
            queryset=qs
        )
        if not filter.form.is_valid():
            raise Exception(filter.form.errors)
        qs = filter.qs
        return qs

    @list_route(serializer_class=ManagerStatsSerializer)
    def get_languages(self, request):
        return Response(data=Country.LANGUAGES)


class RegionFilter(FilterSet):
    search = MethodFilter()
    ids = MultipleMethodFilter()

    class Meta:
        model = Region
        fields = ['name']

    def filter_search(self, queryset, value):
        if not value:
            return queryset
        return queryset.filter(name__icontains=value)

    def filter_ids(self, queryset, value):
        if not value:
            return queryset
        return queryset.filter(pk__in=value)


class RegionViewSet(viewsets.ModelViewSet):
    permission_classes = [HasCRMAccess]
    serializer_class = RegionSerializer
    filter_class = RegionFilter
    ordering = ('name',)

    @classmethod
    def get_base_queryset(cls, params=None, qs=None):
        return Region.objects.all()

    def get_queryset(self):
        qs = self.get_base_queryset(params=self.request.query_params)
        # filters
        filter = self.filter_class(
            data=self.request.query_params,
            queryset=qs
        )
        if not filter.form.is_valid():
            raise Exception(filter.form.errors)
        qs = filter.qs
        return qs
