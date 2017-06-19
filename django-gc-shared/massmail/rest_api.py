# coding=utf-8
from rest_framework import viewsets

from massmail.rest_serializers import CampaignTypeSerializer
from massmail.models import CampaignType


class CampaignTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CampaignType.objects.all()
    serializer_class = CampaignTypeSerializer
    paginator = None
