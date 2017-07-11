# coding=utf-8
from rest_framework import viewsets, filters

from geobase.rest_serializers import CountrySerializer, RegionSerializer
from geobase.models import Country, Region


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CountrySerializer
    filter_backends = (filters.OrderingFilter,)
    ordering = ('weight', 'name')
    paginator = None

    def get_queryset(self):
        return Country.objects.all()


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegionSerializer
    paginator = None

    def get_queryset(self):
        qs = Region.objects.all()
        if 'country' in self.request.query_params:
            qs = qs.filter(country=self.request.query_params['country'])
        return qs
