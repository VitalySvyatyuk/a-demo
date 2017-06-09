# coding=utf-8

from rest_framework import viewsets, mixins

from referral.models import PartnerDomain
from referral.rest_serializers import PartnerDomainSerializer


class PartnerDomainViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    serializer_class = PartnerDomainSerializer
    paginator = None

    def get_queryset(self):
        return self.request.user.partner_domains.all()

    def perform_create(self, serializer):
        instance = serializer.save(
            account=self.request.user,
            api_key=PartnerDomain.generate_api_key(serializer.validated_data['domain'])
        )