# coding=utf-8

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins, viewsets, exceptions
from rest_framework.decorators import detail_route, list_route
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

import notification.models as notification
from log.models import Event
from otp.check import check_otp_drf
from profiles.models import UserDocument, DOCUMENTS_FIELDS
from profiles.rest_serializers import UserSerializer, UserDocumentSerializer
from registration.forms import PasswordResetByPhoneForm

from logging import getLogger
log = getLogger(__name__)


class UserViewSet(viewsets.ReadOnlyModelViewSet, mixins.UpdateModelMixin):
    serializer_class = UserSerializer
    paginator = None

    @detail_route(methods=['post'])
    def change_password(self, request, pk=None):
        from profiles.forms import UserPasswordForm
        user = self.get_object()
        form = UserPasswordForm(user, self.request.data)

        if not form.is_valid():
            raise exceptions.ValidationError(form.errors)

        check_otp_drf('Password change', self.request)
        form.save()

        return Response({'detail': _('Password successfully changed')})

    @list_route(methods=['post'], permission_classes=[])
    def recover_password(self, request):
        """
        Восстановление пароля по SMS
        """
        form = PasswordResetByPhoneForm(self.request.data)

        if not form.is_valid():
            raise exceptions.ValidationError(form.errors)

        form.send_new_password_by_sms()

        return Response({
            'detail': _('Password successfully recovered'),
            'redirect': reverse('password_reset_by_phone_done'),
        })

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.kwargs[lookup_url_kwarg] == 'me':
            self.kwargs[lookup_url_kwarg] = self.request.user.pk
        return get_object_or_404(self.get_queryset(), **{
            self.lookup_field: self.kwargs[lookup_url_kwarg]
        })

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.pk)

    def remove_changed_validations(self, instance, new_data):
        for validation in instance.validations.filter(is_valid=True):
            field = validation.key
            if validation.key in new_data:
                new = new_data[validation.key]
                old = getattr(instance, validation.key)
            elif validation.key in new_data.get('profile', {}):
                new = new_data['profile'][validation.key]
                old = getattr(instance.profile, validation.key)
            else:
                validation.delete()
                continue

            if new != old:
                validation.delete()
                Event.VALIDATION_REVOKED.log(instance, {
                    "field": validation.key
                })

    def get_changes_for_logs(self, instance, new_data):
        changes = {}
        for field, new_value in new_data.iteritems():
            if field in ["email", "username", "first_name", "last_name"] and new_value != getattr(instance, field):
                changes[field] = {
                    "from": getattr(instance, field),
                    "to": new_value
                }
            elif hasattr(instance.profile, field) and new_value != getattr(instance.profile, field):
                changes[field] = {
                    "from": getattr(instance.profile, field),
                    "to": new_value
                }
        return changes

    def perform_update(self, serializer):
        check_otp_drf('Save profile', self.request)
        self.remove_changed_validations(serializer.instance, serializer.validated_data)
        changes = self.get_changes_for_logs(serializer.instance, serializer.validated_data)

        instance = serializer.save()

        instance.profile.update_subscription()

        # try to assign new manager if not taken
        if instance.profile.changes.get('agent_code') and not instance.profile.manager:
            instance.profile.autoassign_manager()
            if instance.profile.manager:
                instance.profile.save()
        Event.PROFILE_CHANGED.log(instance, changes)


class UserDocumentViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    serializer_class = UserDocumentSerializer
    parser_classes = (FormParser, MultiPartParser)
    paginator = None

    def get_queryset(self):
        return UserDocument.objects.filter(user=self.request.user, is_deleted=False)

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        notification.send([self.request.user], 'checkdocument_issue')
        Event.DOCUMENT_UPLOADED.log(instance)

    @list_route()
    def get_fields(self, request):
        return Response(DOCUMENTS_FIELDS)

    @list_route(methods=['post'])
    def bulk_upload(self, request):
        log.info("Bulk upload docs for user %s" % request.user.username)
        log.debug('request data=%s' % request.data)
        resp = []
        try:
            for name, file in request.data.iteritems():
                doc = UserDocument(user=request.user, file=file, name=name)
                doc.clean_fields()
                doc.save()
                resp.append(doc)
        except ValidationError:
            raise exceptions.ValidationError(_("Bad file extension or size!"))

        if not resp:
            raise exceptions.ValidationError(_("No documents uploaded!"))
        else:
            notification.send([self.request.user], 'checkdocument_issue')
            return Response(self.serializer_class(resp, many=True).data)
