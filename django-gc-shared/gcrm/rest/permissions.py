# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from datetime import datetime, timedelta
from rest_framework import permissions
from django.core.mail import send_mail


class HasCRMAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            man = request.user.crm_manager
        except:
            return False
        if not man.is_ip_allowed(request.META['REMOTE_ADDR']):
            return False
        return True


class HasContactsLimit(permissions.BasePermission):
    message = 'Лимит просмотра исчерпан, попробуйте позже'

    def has_object_permission(self, request, view, obj):
        from gcrm.models import ContactUserViewRecord

        lim = datetime.now() - timedelta(hours=10)
        if ContactUserViewRecord.objects.filter(contact=obj, user=request.user, creation_ts__gte=lim).exists():
            return True

        if not request.user.is_superuser:
            if request.user.crm_manager.daily_limit:
                daily_limit = request.user.crm_manager.daily_limit
            else:
                daily_limit = 300
            per_hour = daily_limit / 3.0
            per_ten = per_hour / 5.0

            if ContactUserViewRecord.objects.filter(
                user=request.user, creation_ts__gte=datetime.now() - timedelta(minutes=10)
            ).count() > per_ten:
                self.security_notification(request, '10 minute ({} views)'.format(per_hour), email=False)
                return False

            if ContactUserViewRecord.objects.filter(
                user=request.user, creation_ts__gte=datetime.now() - timedelta(hours=1)
            ).count() > per_hour:
                self.security_notification(request, '1 hour ({} views)'.format(per_hour))
                return False

            if ContactUserViewRecord.objects.filter(
                user=request.user, creation_ts__gte=datetime.now() - timedelta(days=1)
            ).count() > daily_limit:
                self.security_notification(request, 'daily ({} views)'.format(daily_limit))
                return False

        ContactUserViewRecord.objects.create(contact=obj, user=request.user)
        return True

    def security_notification(self, request, limit_type, email=True):
        from log.models import Event
        Event.ACCOUNT_DATA_VIEW_EXCEEDED.log(None, {'limit_type': limit_type})

        if email:
            subject = "%s has exceeded his %s CRM limit" % (request.user.email, limit_type)
            send_mail(
                subject=subject,
                message="At %s %s from IP %s with User-Agent %s" % (
                    datetime.now(), subject,
                    request.META.get('REMOTE_ADDR'),
                    request.META.get('HTTP_USER_AGENT')
                ),
                from_email="info@arumcapital.eu",
                recipient_list=('valexeev@grandcapital.net', 'kozlovsky@grandcapital.net')
            )
