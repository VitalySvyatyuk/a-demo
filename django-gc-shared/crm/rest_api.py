# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date

from rest_framework import viewsets, status
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from log.models import Event

from crm.models import ManagerReassignRequest, PersonalManager
from crm.assignment_logic import possible_clients_for, get_base_clients_qs
from crm.utils import amo_sync_contact, amo_sync_task
from crm.pyamo2 import get_pyamo_api
from crm.rest_permissions import CanGetNewCustomer
from crm.rest_serializers import ManagerSerializer, CustomerSerializer

from telephony.models import CallDetailRecord


def has_reassign_requests_by(user, manager):
    return ManagerReassignRequest.objects.filter(
        author=manager,
        user=user,
        created_at__gte=user.profile.taken_by_manager_at)
MIN_PHONE_NUMBER_LENGTH = 9
MAX_PHONE_NUMBER_LENGTH = 11
# and len(last_assigned_customer.profile.phone_mobile) <= MAX_PHONE_NUMBER_LENGTH \


class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAdminUser,)
    model = User
    serializer_class = CustomerSerializer
    paginator = None

    def get_queryset(self):
        return User.objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg in self.kwargs\
                and self.kwargs.get(lookup_url_kwarg) == 'me':
            self.kwargs[lookup_url_kwarg] = self.request.user.id
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    @list_route(permission_classes=(IsAuthenticated, IsAdminUser, CanGetNewCustomer))
    def get_new(self, request):
        # FIRST OF, check for last client call availability

        last_assigned_customer = request.user \
            .crm_manager.clients_taken.first()

        # we have previous customer
        # and he has valid number
        # and has no requests to change manager:
        # if last_assigned_customer \
        #   and last_assigned_customer.profile.phone_mobile \
        #   and len(last_assigned_customer.profile.phone_mobile) > MIN_PHONE_NUMBER_LENGTH \
        #   and not has_reassign_requests_by(last_assigned_customer, request.user):
        #    manager_to_user_calls = last_assigned_customer \
        #        .profile \
        #        .phone_calls_to \
        #        .from_user(request.user, with_phone=False)

        #    if not manager_to_user_calls.exists():
        #        return Response({
        #            'detail': u"Для получения нового клиента, "
        #                      u"необходимо совершить звонок предыдущему",
        #            'last_customer_link': last_assigned_customer.amo.get_url()
        #        }, status=status.HTTP_403_FORBIDDEN)

        #    if not manager_to_user_calls.answered().exists():
        #        time_passed_since = datetime.now() - last_assigned_customer.profile.taken_by_manager_at
        #        if time_passed_since < timedelta(seconds=30):
        #            left = timedelta(seconds=30) - time_passed_since
        #            return Response({
        #                'detail': u"Клиент будет доступен через {} секунд".format(left),
        #                'last_customer_link': last_assigned_customer.amo.get_url()
        #            }, status=status.HTTP_403_FORBIDDEN)
        if last_assigned_customer:
            # if we have no last_call date, try to find call
            if not last_assigned_customer.profile.last_manager_call_at:
                last_assigned_customer.profile.last_manager_call_at

                last_call = last_assigned_customer \
                   .profile \
                   .phone_calls_to \
                   .from_user(request.user, with_phone=False) \
                   .order_by('-call_date').first()
                if last_call:
                    last_assigned_customer.profile.last_manager_call_at = last_call.call_date
                    last_assigned_customer.profile.save()

            profile = last_assigned_customer.profile
            if not profile.last_manager_call_at or \
                profile.last_manager_call_at < profile.taken_by_manager_at:
                return Response({
                    'detail': u"Для получения нового клиента, "
                              u"необходимо совершить звонок предыдущему",
                    'last_customer_link': last_assigned_customer.amo.get_url()
                }, status=status.HTTP_403_FORBIDDEN)

            time_passed_since = datetime.now() - last_assigned_customer.profile.taken_by_manager_at
            if time_passed_since < timedelta(seconds=10):
                return Response({
                    'detail': "Too fast! slowpoke.jpg"
                }, status=status.HTTP_403_FORBIDDEN)

        # OKAY, give new one
        clients, count = possible_clients_for(request.user)
        if not clients:
            return Response({
                'detail': u"Нет доступных клиентов"
            }, status=status.HTTP_404_NOT_FOUND)

        # okay, now we have client, which we can take
        new_client = clients.first()
        old = new_client.profile.manager
        new_client.profile.set_manager(request.user, taken_by_manager=True)

        try:
            amo = get_pyamo_api()
            amo_sync_contact(amo, new_client.amo)

            task = new_client.amo.add_task(
                "3250", _(u"First contact with the client"), request.user)
            if task:
                amo_sync_task(amo, task)
        except Exception as e:
            # return client back to pool
            new_client.profile.set_manager(None)
            raise e

        new_client.gcrm_contact.add_task(text=_(u"First contact with the client"))

        Event.HAS_BEEN_TAKEN_BY_MANAGER.log(new_client, {
            "old_id": old.id if old else None,
            "old_str": unicode(old),
        })

        return Response({
            'link': new_client.amo.get_url()
        })

    @list_route(permission_classes=(IsAuthenticated, IsAdminUser, CanGetNewCustomer))
    def new_count(self, request):
        from crm.assignment_logic import possible_clients_for
        clients, count = possible_clients_for(request.user)
        return Response(count)

    @detail_route(methods=['get', 'options'])
    def mark_called(self, request, pk=None):
        user = self.get_object()
        user.profile.last_manager_call_at = datetime.now()
        user.profile.save()
        return Response(123)


class InfoViewSet(viewsets.ViewSet):
    permission_classes = (IsAdminUser,)
    paginator = None

    @staticmethod
    def get_info_for(users, fr=None, to=None):
        from crm.utils import seconds_to_string

        data = {}
        data['registered'] = User.objects.all()
        if fr and to:
            data['registered'] = data['registered'].filter(date_joined__gte=fr, date_joined__lt=to)
        data['registered'] = data['registered'].count()

        data['buttonNow'] = get_base_clients_qs()
        if fr and to:
            data['buttonNow'] = data['buttonNow'].filter(date_joined__gte=fr, date_joined__lt=to)
        data['buttonNow'] = data['buttonNow'].count()

        data['taken'] = User.objects.filter(profile__manager__in=users).exclude(profile__taken_by_manager_at=None)
        if fr and to:
            data['taken'] = data['taken'].filter(profile__taken_by_manager_at__gte=fr,
                                                 profile__taken_by_manager_at__lt=to)
        data['taken'] = data['taken'].count()

        data['assigned'] = User.objects.filter(profile__manager__in=users)
        if fr and to:
            data['assigned'] = data['assigned'].filter(profile__assigned_to_current_manager_at__gte=fr,
                                                       profile__assigned_to_current_manager_at__lt=to)
        data['assigned'] = data['assigned'].count()

        data['calls'] = calls = CallDetailRecord.objects.filter(Q(user_a__in=users) | Q(user_b__in=users))
        if fr and to:
            data['calls'] = calls = data['calls'].filter(call_date__gte=fr, call_date__lt=to)
        data['calls'] = data['calls'].count()

        data['calls_duration'] = calls.total_duration()
        data['calls_duration_str'] = seconds_to_string(data['calls_duration'])

        data['calls_answered'] = calls.answered().count()
        data['calls_answered_duration'] = calls.answered().total_duration()
        data['calls_answered_duration_str'] = seconds_to_string(data['calls_answered_duration'])

        data['calls_not_answered'] = calls.not_answered().count()
        data['calls_not_answered_duration'] = calls.not_answered().total_duration()
        data['calls_not_answered_duration_str'] = seconds_to_string(data['calls_not_answered_duration'])
        return data

    @list_route()
    def summary_total(self, request):
        crm_user = request.user.crm_manager
        if crm_user.is_head_supermanager or request.user.is_superuser:
            users = PersonalManager.objects.active().values('user')
        elif crm_user.is_office_supermanager:
            users = PersonalManager.objects.active().filter(office=crm_user.office).values('user')
        else:
            raise PermissionDenied()

        return Response({
            'today': self.get_info_for(users, date.today(), date.today() + timedelta(1)),
            'yesterday': self.get_info_for(users, date.today() - timedelta(1), date.today()),
            'days7': self.get_info_for(users, date.today() - timedelta(7), date.today() + timedelta(1)),
            'month': self.get_info_for(users, date.today().replace(day=1), date.today() + timedelta(1)),
            'year': self.get_info_for(users, date.today().replace(day=1, month=1),
                                      date.today() + timedelta(1)),
            'total': self.get_info_for(users),
        })

    @list_route()
    def summary(self, request):
        return Response({
            'today': self.get_info_for([request.user], date.today(), date.today() + timedelta(1)),
            'yesterday': self.get_info_for([request.user], date.today() - timedelta(1), date.today()),
            'days7': self.get_info_for([request.user], date.today() - timedelta(7), date.today() + timedelta(1)),
            'month': self.get_info_for([request.user], date.today().replace(day=1), date.today() + timedelta(1)),
            'year': self.get_info_for([request.user], date.today().replace(day=1, month=1), date.today() + timedelta(1)),
            'total': self.get_info_for([request.user]),
        })


class ManagersViewSet(viewsets.ReadOnlyModelViewSet):
    model = PersonalManager
    permission_classes = (IsAdminUser,)
    serializer_class = ManagerSerializer
    paginator = None

    def get_queryset(self):
        return PersonalManager.objects.filter(user__is_active=True)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg in self.kwargs\
                and self.kwargs.get(lookup_url_kwarg) == 'me':
            self.kwargs[lookup_url_kwarg] = self.request.user.id
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj
