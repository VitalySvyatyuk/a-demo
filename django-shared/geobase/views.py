# -*- coding: utf-8 -*-

from django.views.decorators.http import require_GET
from django.utils.translation import get_language

from shared.decorators import as_json

from geobase.models import City, Region

@require_GET
@as_json
def autocomplete_region(request):
    qs = Region.objects.all()
    if request.GET.get("country", "").isdigit():
        qs = qs.filter(country__pk=request.GET["country"])
    if get_language() == 'ru':
        return list(qs.values("id", "name")), 200
    else:
        items = list()
        for item in qs:
            items.append({"pk" : item.pk, "name" : item.name_en})

        return items, 200

@require_GET
@as_json
def autocomplete_city(request, limit):
    qs = City.objects.all()

    if request.GET.get("country", "").isdigit():
        qs = qs.filter(country__pk=request.GET["country"])
    if request.GET.get("region", "").isdigit():
        qs = qs.filter(region__pk=request.GET["region"])
    if request.GET.get("term"):
        if get_language() == 'ru':
            qs = qs.filter(name__istartswith=request.GET["term"])
        else:
            qs = qs.filter(name_en__istartswith=request.GET["term"])
    if get_language() == 'ru':
        return list(qs[:int(limit)].values_list("name", flat=True))
    else:
        return list(qs[:int(limit)].values_list("name_en", flat=True))

