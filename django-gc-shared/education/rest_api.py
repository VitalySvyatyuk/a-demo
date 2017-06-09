# -*- coding: utf-8 -*-

from rest_framework import viewsets

from education.rest_serializers import WebinarRegistrationSerializer
from education.models import WebinarRegistration


class WebinarRegistrationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WebinarRegistrationSerializer

    def get_queryset(self):
        return WebinarRegistration.objects.filter(
            user=self.request.user
        ).order_by('-tutorial__starts_at')
